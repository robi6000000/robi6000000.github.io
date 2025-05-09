#### MEAN ANALYSIS ######################################################################
options(width=300)

# zdroj1: https://www.kaggle.com/datasets/josephgreen/anthony-fantano-album-review-dataset?select=albums.csv

rawalbums <- read.csv("statprojekt/fantano_scores.csv")
rawalbums <- rawalbums[, c("album","artist", "date","genre", "score" )]
rawalbums <- rawalbums[order(rawalbums$date),]
head(rawalbums)
rownames(rawalbums) <- NULL
albums <- rawalbums[grepl("^(10|[0-9])$", rawalbums$score), ] #score iba numericke hodnoty
albums$score <- as.numeric(albums$score) #pretypovanie na numericke hodnoty
ratings <- albums$score
dim(albums)

plot(ecdf(ratings))
osX <- seq(0,10,length.out=10000)
lines(osX, pnorm(osX, mean=mean(ratings), sd=sqrt(var(ratings))), col="red")

# TEST NORMALITY
ks.test(ratings, "pnorm", mean = mean(ratings), sd = sd(ratings))
# p-value < 2.2e-16   ->   data niesu normalne

# TESTUJEME:
# H0: mu <= 5	vs 	H1: mu > 5 	
# h0: priemerne hodnotenie je <= 5 vs h1: priemerne hodnotenie je > ako 5
wilcox.test(ratings, alternative = "greater", mu = 5)
# p-value < 2.2e-16   ->   zamietame h0


# Pre porovnanie dvoch priemerov vezmeme priemerne hodnotenie albumov z dvoch najhodnotenejsich albumov:
# (hiphop, pop)
summary(albums)

head(sort(table(albums$genre), decreasing = TRUE), 5)
hiphop <- albums[grepl("hip hop", albums$genre),]
pop <- albums[grepl("pop", albums$genre),]

# TESTUJEME:
# H0: mu1<=mu2 	vs 	H1: mu1>mu2 		
# (h0: hiphop ma priemerny rating <= pop vs h1: hiphop ma > pop)
wilcox.test(hiphop$score, pop$score, alternative = "greater")
# p-value = 0.9998    ->   H0 nezamietame (hiphop <= pop)

mean(hiphop$score) 				#5.851582
mean(pop$score)    				#6.315625

#### CORRELATION ANALYSIS ######################################################################

salaries <- read.table("statprojekt/football-salaries-2017.txt", header = TRUE, sep = "\t")
salaries <- na.omit(salaries)
names(salaries)[names(salaries) == "Salary.total.in..M."] <- "Salary"
names(salaries)[names(salaries) == "Avg.Age"] <- "Age"
attach(salaries)
dim(salaries)

cor(salaries[, c(2,3,5)])
png("001.png", height = 600, width = 600)
plot(salaries[,c(2,3,5)])
dev.off()
# TESTY NORMALITY:
shapiro.test(Wins)
shapiro.test(Age)
shapiro.test(Salary)
# Zamietame normalitu pre Salary

cor(Wins, Age)
# 0.3445676

# TESTUJEME:
# H0: r = 0 	vs 	H1: r != 0
cor.test(Wins, Age, alternative = "two.sided")
# p-value = 0.05346
# nezamietame H0.      ->   	korelacia je zanedbatelna

# H0: rho = 0 	vs 	H1: rho != 0
cor.test(Salary, Wins ,alternative="two.sided", method="spearman")
# nemame dostatocnu informaciu o zamietnuti nulovej hypotezy, korelacie su teda zanedbatelne

# fisher Z:
r <- cor(Wins, Age)
Z <- atanh(r)

# 95% IS: (pre rho)
n <- length(Wins)
L <- (Z - qnorm(.975)/sqrt(n-3))
U <- (Z + qnorm(.975)/sqrt(n-3))
c(L, U) 
# IS: (-0.004689851,  0.723222499)

#otestujeme rovnost dvoch korelacii: salary s poctom vyhier pre nad a podpriemerny plat
mu <- mean(Salary)
aboveAge<-Age[Salary>=mu]
aboveWins <- Wins[Salary>=mu]

d


#H0: obe skupiny maju rovnaku korelaciu vs H1: r1!=r2
r1 <- cor(aboveAge, aboveWins)
r2 <- cor(belowAge, belowWins)
Z1 <- atanh( r1 )
Z2 <- atanh( r2 )
n1 <- length( aboveAge )
n2 <- length( belowAge )
Z12 <- ((Z1-Z2)/sqrt(1/(n1-3) + 1/(n2-3)))
# print(Z12)
p <- 2 * (1 - pnorm(abs(Z12)))
# p_value = 0.2592782     ->    	  nezamietame nulovu hypotezu - nemame dostatocne informacie na to,
# 									  aby sme povedali ze sa dane korelacie signifikantne lisia.

#### LINEAR REGRESSION ######################################################################

water <- read.table("statprojekt/hard-water.txt", header = TRUE, sep = "\t")
water <- na.omit(water)
attach(water)

png("002.png", height = 600, width = 600)
plot(Calcium, Mortality, main="Mortality (per 100 000) vs Calcium (ppm)")

MODEL <- lm(Mortality ~ 1+Calcium,  x=TRUE)  
abline(MODEL, lwd=2)
dev.off()
summary(MODEL)
# Intercept: 1676.3556  (Beta0)
# Calcium:   -3.2261    (Beta1)

ks.test(Mortality, "pnorm", mean = mean(Mortality), sd = sd(Mortality)) #p-value = 0.8968
ks.test(Calcium, "pnorm", mean = mean(Calcium), sd = sd(Calcium))       #p-value = 0.01786 -> nie normalne

png("003.png", height = 600, width = 600)
plot(ecdf(Calcium), main="Empirical CDF of Calcium")
osX <- seq(0 ,150,length.out=10)
lines(osX, pnorm(osX, mean=mean(Calcium), sd=sqrt(var(Calcium))), col="red")
dev.off()
# TEST NORMALITY REZIDUI:
shapiro.test(MODEL$residuals) 		  #p-value = 0.6798 -> residuals su normalne

png("004.png", height = 600, width = 600)
plot(MODEL, which=1, main="Linear regression residuals vs fitted") 	#vykreslime residuals
dev.off()									  
#vykreslime model
png("005.png", height = 600, width = 600)
plot(Calcium, Mortality,main="Mortality (per 100 000) vs Calcium (ppm)")
MODEL <- lm(Mortality ~ 1+Calcium,  x=TRUE)  
abline(MODEL, lwd=2)

# pas spolahlivosti:
Scheffe1 <- function(a,betaHAT,Y,X)
{
	n <- length(Y)					  #pocet zavislych prem
	k <- length(betaHAT)			  #pocet parametrov
	SSe <- sum( (Y - X%*%betaHAT)^2 ) #sucet stvorcov chyb
	S <- sqrt( SSe / (n-k) )

	# Dolna a Horna hranica
	L <- t(a)%*%betaHAT - sqrt(k*qf(0.95,df1=k,df2=n-k))*S*sqrt( t(a)%*%solve(t(X)%*%X)%*%a )
	U <- t(a)%*%betaHAT + sqrt(k*qf(0.95,df1=k,df2=n-k))*S*sqrt( t(a)%*%solve(t(X)%*%X)%*%a )
	return( c(L , U) )
}

osX <- seq(min(Calcium) , max(Calcium) , length.out=150)
okraje.pasu <- matrix( nrow=2 , ncol=length(osX) )
for (i in 1:length(osX))
   okraje.pasu[,i] <- Scheffe1( a=c( 1,osX[i]) , betaHAT=MODEL$coeff , Y=Mortality , X=MODEL$x )

# dolna a horna hranica:
lines(osX , okraje.pasu[1,] ,
      col="red")
lines(osX , okraje.pasu[2,] ,
      col="red")

# predikcny pas:
Scheffe2 <- function(a,betaHAT,Y,X)
{
	n <- length(Y)
	k <- length(betaHAT)
	SSe <- sum( (Y - X%*%betaHAT)^2 )
	S <- sqrt( SSe / (n-k) )

	L <- t(a)%*%betaHAT - sqrt(k*qf(0.95,df1=k,df2=n-k))*S*sqrt(1+t(a)%*%solve(t(X)%*%X)%*%a )
	U <- t(a)%*%betaHAT + sqrt(k*qf(0.95,df1=k,df2=n-k))*S*sqrt(1+t(a)%*%solve(t(X)%*%X)%*%a )
	return( c(L , U) )
}

osX <- seq(min(Calcium) , max(Calcium) , length.out=140)
okraje.pasu <- matrix( nrow=2 , ncol=length(osX) )
for (i in 1:length(osX))
   okraje.pasu[,i] <- Scheffe2( a=c( 1,osX[i]) , betaHAT=MODEL$coeff , Y=Mortality , X=MODEL$x )

#dolna a horna hranica pasu:
lines(osX , okraje.pasu[1,] ,
      col="green")
lines(osX , okraje.pasu[2,] ,
      col="green")

dev.off()
# IS pre kontrast:
ISpreKontrast <- function(a,betaHAT,Y,X)
{
	n <- length(Y)
	k <- length(betaHAT)
	SSe <- sum( (Y - X%*%betaHAT)^2 )
	S <- sqrt( SSe / (n-k) )

	DolnaHranica <- t(a)%*%betaHAT - qt(0.975,df=n-k)*S*sqrt( t(a)%*%solve(t(X)%*%X)%*%a )
	HornaHranica <- t(a)%*%betaHAT + qt(0.975,df=n-k)*S*sqrt( t(a)%*%solve(t(X)%*%X)%*%a )
	return( c(DolnaHranica , t(a)%*%betaHAT , HornaHranica) )
}
betaHAT <- MODEL$coeff
Y <- Mortality
X <- MODEL$x
# a <- c(0,1)
# ISpreKontrast(a,betaHAT,Y,X)
# a <- c(1,0)
# ISpreKontrast(a,betaHAT,Y,X)
# a <- c(1,101)
# ISpreKontrast(a,betaHAT,Y,X)
a <- c(1, -1)  
ISpreKontrast(a, betaHAT, Y, X)


# Predikcny interval:
PredikcnyInterval <- function(a,betaHAT,Y,X)
{
	n <- length(Y)
	k <- length(betaHAT)
	SSe <- sum( (Y - X%*%betaHAT)^2 )
	S <- sqrt( SSe / (n-k) )

	DolnaHranica <- t(a)%*%betaHAT - qt(0.975,df=n-k)*S*sqrt(1+t(a)%*%solve(t(X)%*%X)%*%a )
	HornaHranica <- t(a)%*%betaHAT + qt(0.975,df=n-k)*S*sqrt(1+t(a)%*%solve(t(X)%*%X)%*%a )
	return( c(DolnaHranica , t(a)%*%betaHAT , HornaHranica) )
}

a <- c(0,1)
PredikcnyInterval(a, betaHAT, Y, X)
a <- c(1,0)
PredikcnyInterval(a, betaHAT, Y, X)
a <- c(1,-1)
PredikcnyInterval(a, betaHAT, Y, X)
#############################################################################################
png("006.png", width = 600, height = 600)
plot(Calcium, Mortality,main="Mortality (per 100 000) vs Calcium (ppm)")
cMODEL <- lm(Mortality ~ 1+Calcium+I(Calcium^2),  x=TRUE)  
osX <- seq(min(Calcium) , max(Calcium) , by=10)
lines(osX , cMODEL$coeff[1] + cMODEL$coeff[2]*osX + cMODEL$coeff[3]*osX^2)

osX <- seq(min(Calcium) , max(Calcium) , length.out=150)
okraje.pasu <- matrix( nrow=2 , ncol=length(osX) )
for (i in 1:length(osX))
   okraje.pasu[,i] <- Scheffe1( a=c( 1,osX[i], (osX[i])^2) , betaHAT=cMODEL$coeff , Y=Mortality , X=cMODEL$x )

# dolna a horna hranica:
lines(osX , okraje.pasu[1,] ,
      col="red")
lines(osX , okraje.pasu[2,] ,
      col="red")

osX <- seq(min(Calcium) , max(Calcium) , length.out=140)
okraje.pasu <- matrix( nrow=2 , ncol=length(osX) )
for (i in 1:length(osX))
   okraje.pasu[,i] <- Scheffe2( a=c( 1,osX[i], (osX[i])^2) , betaHAT=cMODEL$coeff , Y=Mortality , X=cMODEL$x )

#dolna a horna hranica pasu:
lines(osX , okraje.pasu[1,] ,
      col="green")
lines(osX , okraje.pasu[2,] ,
      col="green")
dev.off()
summary(cMODEL)
# Residual standard error: 144.1 on 58 degrees of freedom
# Multiple R-squared:  0.4301,    Adjusted R-squared:  0.4104
# F-statistic: 21.88 on 2 and 58 DF,  p-value: 8.302e-08
summary(MODEL)
# Residual standard error: 143 on 59 degrees of freedom
# Multiple R-squared:  0.4288,    Adjusted R-squared:  0.4191
# F-statistic:  44.3 on 1 and 59 DF,  p-value: 1.033e-08

png("000.png", width = 1200, height = 600)

par(mfrow = c(1, 2))
plot(cMODEL, which = 1, main = "Polynomial")
plot(MODEL, which = 1, main = "Linear")
dev.off()
