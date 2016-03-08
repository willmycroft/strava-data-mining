import scrapy
import csv
from isoweek import Week
import re
from Cookie import SimpleCookie


#==============================================================================
# Scraps Strava profiles to obtain an approximation to their weekly mileage
# by analysing the BarChart. Takes two parameters:
# filename - The path to an headered csv file
# id_index - The index of the strava athlete ID in the csv file
# Also reads the athletes all time running and all time cycling distances
# from the sidebar.
# Outputs a list of the following:
# id - The athlete id
# at_run - The athletes all time distance ran
# at_cycle - The atlhetes all time distance cycled
# mileage - A list of date (%Y-%m-%d), mileage tuples covering 52 weeks from
# the current date
#==============================================================================
class StravaSpider(scrapy.Spider):
    name = 'StravaSpider'
    headers = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, sdch',
        'Accept-Language':'en-US,en;q=0.8',
        'Cache-Control':'max-age=0',
        'Connection':'keep-alive',
        'Host':'www.strava.com',
        'If-None-Match':'W/"ceeba81cfb3021b49548db0ea0447e67"',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36'
    }
    xhr_headers = dict(headers)
    xhr_headers["X-Requested-With"] = "XMLHttpRequest"
    
    cookie_string = """<COOKIE STRING HERE>"""
    cookie = SimpleCookie()
    cookie.load(cookie_string)
    cookies = {}
    
    # Even though SimpleCookie is dictionary-like, it internally uses a Morsel object
    # which is incompatible with requests. Manually construct a dictionary instead.
    for key, morsel in cookie.items():
        cookies[key] = morsel.value
    
    
    def __init__(self, filename, id_index):
        self.filename = filename
        self.id_index = int(id_index)
    
    def start_requests(self):
        with open(self.filename, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None) # Skip header
            for row in reader:
                athlete_id = int(row[self.id_index])
                yield scrapy.Request('https://www.strava.com/athletes/' + str(athlete_id),
                                     headers=self.headers,
                                     cookies=self.cookies,
                                     meta={'id': athlete_id})
                    
    
    def parse(self, response):
        # Read in the graph and approximation mileage from the height of the bars
        graph = response.xpath('//div[@class="athlete-graph"]')
        y_max = int(graph.xpath('./ul[@class="y-axis"]/li[last()]/text()').extract()[0])
        bar_divs = graph.xpath('./ul[@class="intervals"]//div[@class="bar"]')
        miles = []
        for div in bar_divs:
        
            style = (div.xpath('.//div[@class="fill"]/@style').extract() or ["0"])[0]
            height = int(re.sub('[^\d]+', '', style)) # The style attribute is e.g "height:83px;"
            miles.append(y_max*height/100.0)
            
        weeks = graph.xpath('./ul[@class="intervals"]/li/@id').extract()
        # Data returns e.g. interval-201605
        # Example: 201605 = 5th week in 2016
        wb_dates = map(lambda x : Week(int(x[9:13]),int(x[-2:])).monday().strftime('%Y-%m-%d'), weeks) 

            
        # Get sidebar, but propagate this data through so we can yield:
        yield scrapy.Request('https://www.strava.com/athletes/' +
                            str(response.meta['id']) + 
                            '/profile_sidebar_comparison',
                            callback=self.parse_sidebar,
                            headers=self.xhr_headers,
                            meta={'id': response.meta['id'],
                                   'mileage': zip(wb_dates, miles)})        
            
    def parse_sidebar(self, response):       
        
        at_run_tbody = response.xpath('//div[@class="running hidden"]//tbody[position() = last() - 1]')[0]
        # If privacy settings are not on then the penultimate
        # tbody is all time, otherwise it is year to date and the last tbody
        # is all time.
        if at_run_tbody.xpath('./@id').extract() == ["running-ytd"]:
            at_run_tbody = response.xpath('//div[@class="running hidden"]//tbody[position() = last()]')[0]

        all_time_running = float(re.sub('[^\d.]+', '', at_run_tbody.xpath('./tr[2]/td[2]/text()').extract()[0]))
        all_time_cycling = float(re.sub('[^\d.]+', '', response.xpath('//div[@class="cycling hidden"]//tbody[last()]/tr[2]/td[2]/text()').extract()[0]))
        
        dictionary = {
            'id': response.meta['id'],
            'mileage': response.meta['mileage'],
            'at_run': all_time_running,
            'at_cycle': all_time_cycling
        }  
        yield dictionary
        


        

        