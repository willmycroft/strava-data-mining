library(ggplot2)
library(stringr)

df <- data.frame(read.csv("data/leeds.cleaned.csv"))

# Colours to use
col <- rgb(0,191/255,196/255)
col2 <- rgb(248/255,118/255,109/255)

# Summary of data
summary(df)

# Mark those who do a lot of cycling
CYCLING_THRESHOLD = 0.2
df$cyclist = factor(ifelse(df$at_cycle > CYCLING_THRESHOLD*df$at_run, "Cyclist", "Runner"))
runners <- subset(df, cyclist=="Runner" & sex %in% c("M", "F"))

# Summary of runners
summary(runners)

# Plot all data
ggplot(df, aes(x=X6_week_avg, y=time)) + 
  labs(x="6 Week Average Mileage",y="Time") +
  ggtitle("2015 Leeds Abbey Dash") + 
  geom_point(aes(colour=cyclist)) +
  scale_y_continuous(labels=function(x) { paste(floor(x/60), ":", str_pad(x %% 60, 2, "left", "0"), sep="") }) +
  theme_classic() +
  theme(legend.title=element_blank())

# Plot runners
ggplot(runners, aes(x=X6_week_avg, y=time)) + 
  labs(x="6 Week Average Mileage",y="Time") +
  ggtitle("Runners at Leeds Abbey Dash 2015") + 
  geom_point(aes(colour=sex)) +
  scale_y_continuous(labels=function(x) { paste(floor(x/60), ":", str_pad(x %% 60, 2, "left", "0"), sep="") }) +
  theme_classic()

# Plot faster men and faster women
M_CUTOFF = 40*60
W_CUTOFF = 50*60
fast_runners <- subset(runners, (time<M_CUTOFF & sex=="M") | (time<W_CUTOFF & sex=="F"))
summary(fast_runners)

ggplot(fast_runners, aes(x=X6_week_avg, y=time)) + 
  labs(x="6 Week Average Mileage",y="Time") +
  ggtitle("Faster Runners at Leeds Abbey Dash 2015") + 
  geom_point(aes(colour=sex)) +
  scale_y_continuous(labels=function(x) { paste(floor(x/60), ":", str_pad(x %% 60, 2, "left", "0"), sep="") }) +
  theme_classic()

# Perform a simple linear regression on the faster runners: time = a.mileage + b

m_reg <- with(subset(fast_runners, sex=="M"), {lm(time~X6_week_avg)})
f_reg <- with(subset(fast_runners, sex=="F"), {lm(time~X6_week_avg)})

# Output regression
m_reg
f_reg

# Plot regression
ggplot(fast_runners, aes(x=X6_week_avg, y=time)) + 
  labs(x="6 Week Average Mileage",y="Time") +
  ggtitle("Faster Runners at Leeds Abbey Dash 2015") + 
  geom_point(aes(colour=sex)) +
  geom_abline(intercept=m_reg$coefficients[[1]], slope=m_reg$coefficients[[2]], colour=col) +
  geom_abline(intercept=f_reg$coefficients[[1]], slope=f_reg$coefficients[[2]], colour=col2) +
  scale_y_continuous(labels=function(x) { paste(floor(x/60), ":", str_pad(x %% 60, 2, "left", "0"), sep="") }) +
  theme_classic()

# Table of mileage and predicted times
predictions <- data.frame(mileage = seq(0,100, 10))
predictions$male <- predict(m_reg, data.frame(X6_week_avg = seq(0,100,10)))
predictions$female <- predict(f_reg, data.frame(X6_week_avg = seq(0,100,10)))
predictions


# Plot residuals
# Male
ggplot(subset(fast_runners, sex=="M"), aes(x=X6_week_avg, y=m_reg$residuals)) +
  ggtitle("Residuals for male faster runners") + 
  labs(x="Average Mileage",y="Residuals") + 
  geom_point(colour=col) + 
  theme_classic()

# QQ plot
qqnorm(m_reg$residuals)

# Normal for comparison
qqnorm(rnorm(length(m_reg$residuals))) 

# Female
ggplot(subset(fast_runners, sex=="F"), aes(x=X6_week_avg, y=f_reg$residuals)) +
  ggtitle("Residuals for female faster runners") + 
  labs(x="Average Mileage",y="Residuals") + 
  geom_point(colour=col) + 
  theme_classic()

# QQ plot
qqnorm(f_reg$residuals)

# Normal for comparison
qqnorm(rnorm(length(f_reg$residuals)))


# Perform a regression on all runners with time = a.log(mileage) + b
MIN_MILEAGE = 5
all_runners <- subset(runners, X6_week_avg > MIN_MILEAGE)
m_runners <- subset(all_runners, sex=="M")
f_runners <- subset(all_runners, sex=="F")

# Do a linear regression on all runners: y = a.log(mileage) + b
m_logreg <- with(m_runners, {lm(time~log(X6_week_avg))})
f_logreg <- with(f_runners, {lm(time~log(X6_week_avg))})

m_curve <- data.frame(x = MIN_MILEAGE:max(m_runners$X6_week_avg),
                            y=predict(m_logreg, data.frame(X6_week_avg = MIN_MILEAGE:max(m_runners$X6_week_avg))))
f_curve <- data.frame(x = MIN_MILEAGE:max(f_runners$X6_week_avg),
                      y=predict(f_logreg, data.frame(X6_week_avg = MIN_MILEAGE:max(f_runners$X6_week_avg))))

# Plot
ggplot(all_runners, aes(x=X6_week_avg, y=time)) + 
  labs(x="6 Week Average Mileage",y="Time") +
  ggtitle("Runners at Leeds Abbey Dash 2015") + 
  geom_point(aes(colour=sex)) +
  geom_line(data=m_curve, aes(x, y), colour=col) +
  geom_line(data=f_curve, aes(x, y), colour=col2) +
  scale_y_continuous(labels=function(x) { paste(floor(x/60), ":", str_pad(x %% 60, 2, "left", "0"), sep="") }) +
  theme_classic()

# Residuals
# Male
ggplot(m_runners, aes(x=log(X6_week_avg), y=m_logreg$residuals)) +
  ggtitle("Residuals for male runners") + 
  labs(x="log(Average Mileage)",y="Residuals") + 
  geom_point(colour=col) + 
  theme_classic()

# Female
ggplot(f_runners, aes(x=log(X6_week_avg), y=f_logreg$residuals)) +
  ggtitle("Residuals for female runners") + 
  labs(x="log(Average Mileage)",y="Residuals") + 
  geom_point(colour=col) + 
  theme_classic()

# We have heteroskadesicity, so peform weighted linear regressions to handle this:

m_weightreg <- with(m_runners, {lm(time~log(X6_week_avg), weights=1/log(X6_week_avg))})
f_weightreg <- with(f_runners, {lm(time~log(X6_week_avg), weights=1/log(X6_week_avg))})
m_weightreg
f_weightreg

m_wcurve <- data.frame(x = MIN_MILEAGE:max(m_runners$X6_week_avg),
                      y=predict(m_weightreg, data.frame(X6_week_avg = MIN_MILEAGE:max(m_runners$X6_week_avg))))
f_wcurve <- data.frame(x = MIN_MILEAGE:max(f_runners$X6_week_avg),
                      y=predict(f_weightreg, data.frame(X6_week_avg = MIN_MILEAGE:max(f_runners$X6_week_avg))))

# Plot
ggplot(all_runners, aes(x=X6_week_avg, y=time)) + 
  labs(x="6 Week Average Mileage",y="Time") +
  ggtitle("Runners at Leeds Abbey Dash 2015") + 
  geom_point(aes(colour=sex)) +
  geom_line(data=m_wcurve, aes(x, y), colour=col) +
  geom_line(data=f_wcurve, aes(x, y), colour=col2) +
  scale_y_continuous(labels=function(x) { paste(floor(x/60), ":", str_pad(x %% 60, 2, "left", "0"), sep="") }) +
  theme_classic()

# Table of mileage and predicted times
predictions2 <- data.frame(mileage = seq(0,100, 10))
predictions2$male <- predict(m_weightreg, data.frame(X6_week_avg = seq(0,100,10)))
predictions2$female <- predict(f_weightreg, data.frame(X6_week_avg = seq(0,100,10)))
predictions2



