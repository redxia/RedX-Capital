tangency.portfolio <- 
  function(er,cov.mat,risk.free, shorts=TRUE)
  {
    # compute tangency portfolio
    #
    # inputs:
    # er				   N x 1 vector of expected returns
    # cov.mat		   N x N return covariance matrix
    # risk.free		 scalar, risk-free rate
    # shorts          logical, allow shorts is TRUE
    #
    # output is portfolio object with the following elements
    # call			  captures function call
    # er				  portfolio expected return
    # sd				  portfolio standard deviation
    # weights		 N x 1 vector of portfolio weights
    call <- match.call()
    
    #
    # check for valid inputs
    #
    asset.names <- names(er)
    if(risk.free < 0)
      stop("Risk-free rate must be positive")
    er <- as.vector(er)
    cov.mat <- as.matrix(cov.mat)
    N <- length(er)
    if(N != nrow(cov.mat))
      stop("invalid inputs")
    if(any(diag(chol(cov.mat)) <= 0))
      stop("Covariance matrix not positive definite")
    # remark: could use generalized inverse if cov.mat is positive semi-definite
    
    #
    # compute global minimum variance portfolio
    #
    gmin.port <- globalMin.portfolio(er, cov.mat, shorts=shorts)
    if(gmin.port$er < risk.free)
      stop("Risk-free rate greater than avg return on global minimum variance portfolio")
    
    # 
    # compute tangency portfolio
    #
    if(shorts==TRUE){
      cov.mat.inv <- solve(cov.mat)
      w.t <- cov.mat.inv %*% (er - risk.free) # tangency portfolio
      w.t <- as.vector(w.t/sum(w.t))	# normalize weights
    } else if(shorts==FALSE){
      Dmat <- 2*cov.mat
      dvec <- rep.int(0, N)
      er.excess <- er - risk.free
      Amat <- cbind(er.excess, diag(1,N))
      bvec <- c(1, rep(0,N))
      result <- solve.QP(Dmat=Dmat,dvec=dvec,Amat=Amat,bvec=bvec,meq=1)
      w.t <- round(result$solution/sum(result$solution), 6)
    } else {
      stop("Shorts needs to be logical. For no-shorts, shorts=FALSE.")
    }
    
    names(w.t) <- asset.names
    er.t <- crossprod(w.t,er)
    sd.t <- sqrt(t(w.t) %*% cov.mat %*% w.t)
    tan.port <- list("call" = call,
                     "er" = as.vector(er.t),
                     "sd" = as.vector(sd.t),
                     "weights" = w.t)
    class(tan.port) <- "portfolio"
    tan.port
  }

globalMin.portfolio <-
  function(er, cov.mat, shorts=TRUE)
  {
    # Compute global minimum variance portfolio
    #
    # inputs:
    # er				N x 1 vector of expected returns
    # cov.mat		N x N return covariance matrix
    # shorts          logical, allow shorts is TRUE
    #
    # output is portfolio object with the following elements
    # call			original function call
    # er				portfolio expected return
    # sd				portfolio standard deviation
    # weights		N x 1 vector of portfolio weights
    call <- match.call()
    
    #
    # check for valid inputs
    #
    asset.names <- names(er)
    er <- as.vector(er)					# assign names if none exist
    cov.mat <- as.matrix(cov.mat)
    N <- length(er)
    if(N != nrow(cov.mat))
      stop("invalid inputs")
    if(any(diag(chol(cov.mat)) <= 0))
      stop("Covariance matrix not positive definite")
    # remark: could use generalized inverse if cov.mat is positive semi-definite
    
    #
    # compute global minimum portfolio
    #
    if(shorts==TRUE){
      cov.mat.inv <- solve(cov.mat)
      one.vec <- rep(1,N)
      w.gmin <- rowSums(cov.mat.inv) / sum(cov.mat.inv)
      w.gmin <- as.vector(w.gmin)
    } else if(shorts==FALSE){
      Dmat <- 2*cov.mat
      dvec <- rep.int(0, N)
      Amat <- cbind(rep(1,N), diag(1,N))
      bvec <- c(1, rep(0,N))
      result <- solve.QP(Dmat=Dmat,dvec=dvec,Amat=Amat,bvec=bvec,meq=1)
      w.gmin <- round(result$solution, 6)
    } else {
      stop("shorts needs to be logical. For no-shorts, shorts=FALSE.")
    }
    
    names(w.gmin) <- asset.names
    er.gmin <- crossprod(w.gmin,er)
    sd.gmin <- sqrt(t(w.gmin) %*% cov.mat %*% w.gmin)
    gmin.port <- list("call" = call,
                      "er" = as.vector(er.gmin),
                      "sd" = as.vector(sd.gmin),
                      "weights" = w.gmin)
    class(gmin.port) <- "portfolio"
    gmin.port
  }

efficient.frontier <- 
  function(er, cov.mat, nport=20, alpha.min=-0.5, alpha.max=1.5, shorts=TRUE)
  {
    # Compute efficient frontier with no short-sales constraints
    #
    # inputs:
    # er			  N x 1 vector of expected returns
    # cov.mat	  N x N return covariance matrix
    # nport		  scalar, number of efficient portfolios to compute
    # shorts          logical, allow shorts is TRUE
    #
    # output is a Markowitz object with the following elements
    # call		  captures function call
    # er			  nport x 1 vector of expected returns on efficient porfolios
    # sd			  nport x 1 vector of std deviations on efficient portfolios
    # weights 	nport x N matrix of weights on efficient portfolios 
    call <- match.call()
    
    #
    # check for valid inputs
    #
    asset.names <- names(er)
    er <- as.vector(er)
    N <- length(er)
    cov.mat <- as.matrix(cov.mat)
    if(N != nrow(cov.mat))
      stop("invalid inputs")
    if(any(diag(chol(cov.mat)) <= 0))
      stop("Covariance matrix not positive definite")
    
    #
    # create portfolio names
    #
    port.names <- rep("port",nport)
    ns <- seq(1,nport)
    port.names <- paste(port.names,ns)
    
    #
    # compute global minimum variance portfolio
    #
    cov.mat.inv <- solve(cov.mat)
    one.vec <- rep(1, N)
    port.gmin <- globalMin.portfolio(er, cov.mat, shorts)
    w.gmin <- port.gmin$weights
    
    if(shorts==TRUE){
      # compute efficient frontier as convex combinations of two efficient portfolios
      # 1st efficient port: global min var portfolio
      # 2nd efficient port: min var port with ER = max of ER for all assets
      er.max <- max(er)
      port.max <- efficient.portfolio(er,cov.mat,er.max)
      w.max <- port.max$weights    
      a <- seq(from=alpha.min,to=alpha.max,length=nport)			# convex combinations
      we.mat <- a %o% w.gmin + (1-a) %o% w.max	# rows are efficient portfolios
      er.e <- we.mat %*% er							# expected returns of efficient portfolios
      er.e <- as.vector(er.e)
    } else if(shorts==FALSE){
      we.mat <- matrix(0, nrow=nport, ncol=N)
      we.mat[1,] <- w.gmin
      we.mat[nport, which.max(er)] <- 1
      er.e <- as.vector(seq(from=port.gmin$er, to=max(er), length=nport))
      for(i in 2:(nport-1)) 
        we.mat[i,] <- efficient.portfolio(er, cov.mat, er.e[i], shorts)$weights
    } else {
      stop("shorts needs to be logical. For no-shorts, shorts=FALSE.")
    }
    
    names(er.e) <- port.names
    cov.e <- we.mat %*% cov.mat %*% t(we.mat) # cov mat of efficient portfolios
    sd.e <- sqrt(diag(cov.e))					# std devs of efficient portfolios
    sd.e <- as.vector(sd.e)
    names(sd.e) <- port.names
    dimnames(we.mat) <- list(port.names,asset.names)
    
    # 
    # summarize results
    #
    ans <- list("call" = call,
                "er" = er.e,
                "sd" = sd.e,
                "weights" = we.mat)
    class(ans) <- "Markowitz"
    ans
  }


efficient.portfolio <-
  function(er, cov.mat, target.return, shorts=TRUE)
  {
    # compute minimum variance portfolio subject to target return
    #
    # inputs:
    # er					    N x 1 vector of expected returns
    # cov.mat  			  N x N covariance matrix of returns
    # target.return	  scalar, target expected return
    # shorts          logical, allow shorts is TRUE
    #
    # output is portfolio object with the following elements
    # call				    original function call
    # er					    portfolio expected return
    # sd					    portfolio standard deviation
    # weights			    N x 1 vector of portfolio weights
    #
    call <- match.call()
    
    #
    # check for valid inputs
    #
    asset.names <- names(er)
    er <- as.vector(er)					# assign names if none exist
    N <- length(er)
    cov.mat <- as.matrix(cov.mat)
    if(N != nrow(cov.mat))
      stop("invalid inputs")
    if(any(diag(chol(cov.mat)) <= 0))
      stop("Covariance matrix not positive definite")
    # remark: could use generalized inverse if cov.mat is positive semidefinite
    
    #
    # compute efficient portfolio
    #
    if(shorts==TRUE){
      ones <- rep(1, N)
      top <- cbind(2*cov.mat, er, ones)
      bot <- cbind(rbind(er, ones), matrix(0,2,2))
      A <- rbind(top, bot)
      b.target <- as.matrix(c(rep(0, N), target.return, 1))
      x <- solve(A, b.target)
      w <- x[1:N]
    } else if(shorts==FALSE){
      Dmat <- 2*cov.mat
      dvec <- rep.int(0, N)
      Amat <- cbind(rep(1,N), er, diag(1,N))
      bvec <- c(1, target.return, rep(0,N))
      result <- solve.QP(Dmat=Dmat,dvec=dvec,Amat=Amat,bvec=bvec,meq=2)
      w <- round(result$solution, 6)
    } else {
      stop("shorts needs to be logical. For no-shorts, shorts=FALSE.")
    }
    
    #
    # compute portfolio expected returns and variance
    #
    names(w) <- asset.names
    er.port <- crossprod(er,w)
    sd.port <- sqrt(w %*% cov.mat %*% w)
    ans <- list("call" = call,
                "er" = as.vector(er.port),
                "sd" = as.vector(sd.port),
                "weights" = w) 
    class(ans) <- "portfolio"
    ans
  }
