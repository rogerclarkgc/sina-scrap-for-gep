TEST_SHAPE <- c(600, 600)
R_MAX = 600
R_MIN = 10
STEP = 10

cat('shape of matrix:', TEST_SHAPE[1], TEST_SHAPE[2], '\n')
test_matrix <- matrix(rnorm(TEST_SHAPE[1]*TEST_SHAPE[2]), nrow=TEST_SHAPE[1])
cat('processing svd...\n')
test_matrix.svd <- svd(test_matrix)
d <- diag(test_matrix.svd$d)
v <- as.matrix(test_matrix.svd$v)
u <- test_matrix.svd$u

r_seq <- seq(R_MIN, R_MAX, STEP)
mean_step <- c()
sd_step <- c()
index <- 1
for(r in r_seq){
  cat("starting reshape in :", r, '\n')
  r_ch <- sample(1:R_MAX, r)
  u1 <- as.matrix(u[, r_ch])
  d1 <- as.matrix(d[r_ch, r_ch])
  v1 <- as.matrix(v[, r_ch])
  test_matrix.after <- u1 %*% d1 %*% t(v1)
  mean_step[index] <- mean(test_matrix.after)
  sd_step[index] <- sd(test_matrix.after)
  index <- index + 1
}
plot(x=r_seq, y=sd_step, ylim=c(0, 1.5), type='l', lwd=1.5, col='blue', xlab='R',ylab='sd')
abline(h=sd(test_matrix), lty=3, lwd=1.5, col='red')
dev.new()
plot(x=r_seq, y=mean_step, type='b', lwd=1.5, col='blue', xlab='R', ylab='mean')
abline(h=mean(test_matrix), lty=3, lwd=1.5, col='red')

