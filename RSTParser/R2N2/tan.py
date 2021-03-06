from nltk import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import nltk
import os
from collections import defaultdict, Counter
from sets import Set
import sklearn
from sklearn import svm
from sklearn import linear_model
import numpy as np
import scipy as sci
import timeit
import sys
sys.path.append('../')
from nltk.stem import WordNetLemmatizer
from buildtree import *
from datastructure import *
from util import *
from model import ParsingModel
from evalparser import *

from math import pow
from numpy import linalg as LA
from math import fabs
from scipy import sparse
import numpy, sys
import numpy, gzip, sys
from numpy.linalg import norm
from util import *
from cPickle import load, dump
rng = numpy.random.RandomState(1234)

class LR():
    def __init__(self, alpha,lmbda,maxiter,size):
        self.alpha = float(alpha) # learning rate for gradient ascent
        self.lmbda = float(lmbda) # regularization constant
        self.epsilon = 0.00001 # convergence measure
        self.maxiter = int(maxiter) # the maximum number of iterations through the data before stopping
        self.threshold = 0.5 # the class prediction threshold
        self.theta = np.zeros(size, dtype='float')
   
    def tanh(self,X):
        return np.tanh(X)
    
    def tanh_grad(self,X):
        return 1. / np.square(np.cosh(X))
    
    def sigmoid(self,x):
        x= 1. / (1. + np.exp(-x))
        return x

    def get_theta(self):
        return self.theta
    def getDataFiles(self,files,train, vocab , vocab_no,rev_vocab):
    
        rows = []
        cols = []
        data = []
        pol = []
        review_sum = count = tp = fp = fn = 0
        folds = ['neg','pos']
       # path = "../../Movies/edu-input-final/"
       
    #     files = [os.path.join(path, fname) for fname in os.listdir(path) if fname.endswith('.edus')]
        for filename in files:
                # filename = (filename.split(".edus"))[0]
                
                f = open(filename, 'r')
                content = f.read()
                # print content
                content = content.decode('utf-8').encode('ascii','ignore')
                content = content.replace('<br />','').lower()
                words = word_tokenize(content)
                words2 = [w for w in words if not w in stopwords.words('english')]
                cnt = Counter(words2)
                for word in cnt:
                    if word not in vocab and train:    
                        vocab[word] = vocab_no[0]
                        rev_vocab[vocab_no[0]] = word
                        vocab_no[0] = vocab_no[0] + 1
                    if word in vocab:
                        rows.append(count)
                        cols.append(vocab[word])
                        data.append(cnt[word])
                

                fname = str(filename.split("/")[-1])
        
                rating = int(fname.split(".")[0].split("_")[1])
                if rating <6:
                    pol.append(-1)
                if rating >6 :
                    pol.append(1)
                    
                count = count + 1
                f.close()
        mat = sci.sparse.csr_matrix((data,(rows,cols)), shape=(count,vocab_no[0])).todense()
        return mat, pol


    def fit(self, X, y,test_mat,test_pol):
        """
        This function optimizes the parameters for the logistic regression classification model from training 
        data using learning rate alpha and regularization constant lmbda
        @post: parameter(theta) optimized by gradient descent
        """
        # X = self.add_ones(X_) # prepend ones to training set for theta_0 calculations
        
        # initialize optimization arrays
        self.n = X.shape[1] # the number of features
        self.m = X.shape[0] # the number of instances
        self.probas = np.zeros(self.m, dtype='float') # stores probabilities generated by the logistic function
       # stores the model theta
        self.lw = np.zeros(self.m, dtype='float')
        self.theta = np.zeros(self.n, dtype='float')
        # iterate through the data at most maxiter times, updating the theta for each feature
        # also stop iterating if error is less than epsilon (convergence tolerance constant)
        print "iter | magnitude of the gradient"
        
        for iteration in xrange(self.maxiter):
            # calc probabilities
            self.lw = self.get_der(X,y)
            # self.probas = self.get_proba(X)
            print iteration
            # print self.lw.shape
            # print X.T.shape

            # print self.probas
            # # calculate the gradient and update theta
            # c= self.probas -y
            c= self.lw
            # print "Cshape",c.shape
            # print c
            # print self.lw
            
            # if y < 0:
            #     y=0
            k = (1.0/self.m) * np.dot(X.T,c.T)
            k=k.T
            # print k.shape
            gw = np.zeros(k.shape[1], dtype='float')
            for i in range(k.shape[1]):
                # print k[i,0]
                gw[i]=k[0,i] 
            # print "GW",gw.shape
            # print gw[0:10]
            # print self.theta[0:10]
            # print gw
            # g0 = gw[0] # save the theta_0 gradient calc before regularization
           
            gw =gw + (self.lmbda * self.theta)/self.m  # regularize using the lmbda term
            # gw[0] = g0 # restore regularization independent theta_0 gradient calc
          
            self.theta -= self.alpha * gw # update parameters
           
            # calculate the magnitude of the gradient and check for convergence
            loss = np.linalg.norm(gw)
            if self.epsilon > loss:
                break
            print "Accuracy" , ":", self.compute_accuracy(test_pol,self.predict(test_mat))
            print iteration, ":", loss

    def get_der(self,X,label):
        iscore = np.dot(X, self.theta)
        # print iscore
        score = self.tanh(iscore)
      # score= iscore
        score =score.T
        # score = iscore.T 
        # print "Score******"
        # print iscore
        # print score
        fscore = np.zeros(score.shape[0], dtype='float')
        for i in range(score.shape[0]):
                 # print k[i,0]
                 fscore[i]=score[i,0] 
        # print "fscore" ,fscore.shape
        # print fscore
        check = 1.0- label*fscore
        # print "Check" , check.shape
        # print check
        check[check<0] = 0
        check[check>0] = 1
        # print "heck"
        # print check
        gradscore = self.tanh_grad(score).T
        # # print gradscore
        gscore = np.zeros(gradscore.shape[1], dtype='float')
        for i in range(gradscore.shape[1]):
                  # print k[i,0]
                  gscore[i]=gradscore[0,i] 
        
        # print "Gscore" , gscore.shape
        # print gscore
        fcore= gscore*label
        der = -check*fcore
        # print der.shape
        fder = np.zeros((1,der.shape[0]), dtype='float')
        for i in range(der.shape[0]):
                 # print k[i,0]
                 fder[0,i]=der[i] 
        # *gscore
        # print der
        # print "Der",der.shape
        # print fder.shape
        return fder

    def get_proba(self, X):
        return 1.0 / (1 + np.exp(- np.dot(X, self.theta)))

    def predict_proba(self, X):
        """
        Returns the set of classification probabilities based on the model theta.
        @parameters: X - array-like of shape = [n_samples, n_features]
                     The input samples.
        @returns: y_pred - list of shape = [n_samples]
                  The probabilities that the class label for each instance is 1 to standard output.
        """
        # X_ = self.add_ones(X)
        return self.get_proba(X)
    
    def score(self,X):
        return self.tanh(np.dot(X, self.theta))

    def predict(self, X):
        """
        Classifies a set of data instances X based on the set of trained feature theta.
        @parameters: X - array-like of shape = [n_samples, n_features]
                     The input samples.
        @returns: y_pred - list of shape = [n_samples]
                  The predicted class label for each instance.
        """
        y_pred =[]
        pred =  self.predict_proba(X)
       
        for i in range(pred.shape[1]):
            proba =pred[0,i] 
            if proba >self.threshold:
                y_pred.append(1)
            else:
                y_pred.append(-1)
        # y_pred = [proba > self.threshold for proba in self.predict_proba(X)]
        return y_pred

    def add_ones(self, X):
        # prepend a column of 1's to dataset X to enable theta_0 calculations
        # print X.shape[0]
        return np.hstack((np.zeros(shape=(X.shape[0],1), dtype='float') + 1, X))

    def sigmoid_grad(self,f):
        sig = sigmoid(f)
        return sig * (1 - sig)
   
    def compute_accuracy(self,y_test, y_pred):
        """
        @returns: The precision of the classifier, (correct labels / instance count)
        """
        correct = 0
        for i in range(len(y_test)):
            if y_pred[i] == y_test[i]:
                correct += 1
        return float(correct) / len(y_test)
    
def savemodel(fname,D):
        """ Save model into fname
        """
        if not fname.endswith('.pickle.gz'):
            fname = fname + '.pickle.gz'
        # D = self.getparams()
        with gzip.open(fname, 'w') as fout:
            dump(D, fout)
        print 'Save model into file {}'.format(fname)


def loadmodel( fname):
        """ Load model from fname
        """
        with gzip.open(fname, 'r') as fin:
            D = load(fin)
        return D
        print 'Load model from file: {}'.format(fname)       

if __name__ == '__main__':
    path = "../../../Movies//sf/out/"
    files = [os.path.join(path, fname) for fname in os.listdir(path) if fname.endswith('.txt')]
    tfiles = files
    # [0:5000]
    print len(tfiles)

    # vfiles = files[0:50] + files[950:] 
    path = "../../../Movies//sf/outtest/"
    files = [os.path.join(path, fname) for fname in os.listdir(path) if fname.endswith('.txt')]
    # tfiles = tfiles + files[50:950]
    vfiles = files[0:5000]
    print len(vfiles)

    # path = "../../../Movies//start/train/pos/"
    # files = [os.path.join(path, fname) for fname in os.listdir(path) if fname.endswith('.txt')]
    # tfiles = files[0:10000] 
    # # vfiles = files[950:1000]
    # path = "../../../Movies//start/train/neg/"
    # files = [os.path.join(path, fname) for fname in os.listdir(path) if fname.endswith('.txt')]
    # tfiles = tfiles + files[0:10000]
    # # vfiles = vfiles + files[950:1000]

    # path = "../../../Movies//start/test/pos/"
    # files = [os.path.join(path, fname) for fname in os.listdir(path) if fname.endswith('.txt')]
    # # tfiles = files[0:500] 
    # vfiles = files[0:10000]
    # path = "../../../Movies//start/test/neg/"
    # files = [os.path.join(path, fname) for fname in os.listdir(path) if fname.endswith('.txt')]
    # # tfiles = tfiles + files[0:500]
    # vfiles = vfiles + files[0:10000]
    print len(tfiles)
    print len(vfiles)
   
  
    # path = "../../../Movies/Bigger-set//"
    # tfiles = [os.path.join(path, fname) for fname in os.listdir(path) if fname.endswith('.txt')]
    # path = "../../../Movies/edu-input-final/"
    # vfiles = [os.path.join(path, fname) for fname in os.listdir(path) if fname.endswith('.txt')]
    print "start"
    alpha=1.0
    lmbda=.1
    maxiter=500
    lr = LR(alpha,lmbda,maxiter,0)
    # theta = defaultdict(int)
    vocab  = defaultdict()
    vocab_no = Counter()
    rev_vocab = defaultdict()
    train_mat,train_pol = lr.getDataFiles(tfiles,True,vocab,vocab_no,rev_vocab)
    test_mat,test_pol = lr.getDataFiles(vfiles,False,vocab,vocab_no,rev_vocab)
    # print test_pol
   
    # D = {"tdata":train_mat, "tpos":train_pol}
    # savemodel("data-sd.pickle.gz",D)
    # D={"vdata":test_mat,"vpos":test_pol}
    # savemodel("data-sdtest.pickle.gz",D)
    # D =loadmodel("data.pickle.gz")
    # train_mat,train_pol  = D["tdata"] ,D["tpos"]
    # prob_train =[]
    # for i in range(len(train_pol)):
    #      if train_pol[i] < 0:
    #          prob_train.append(0)
    #      else:
    #          prob_train.append(1)


    # test_mat,test_pol = D["vdata"] , D["vpos"]
    print test_pol
    # lr = LR(alpha,lmbda,maxiter,train_mat.shape[1])
    # for i in range(10):
        # print lr.score(train_mat)
    lr.fit(train_mat,train_pol,test_mat,test_pol)
        
    y_pred = lr.predict(test_mat)

    print lr.compute_accuracy(test_pol,y_pred)
    print lr.score(test_mat)
    theta =  lr.get_theta()
    words = defaultdict()
    # vocab =  D["vocab"]
    # vocab_no = D["vocabno"]
    # rev_vocab = D["rev_vocab"]
    for i in range(len(theta)):
         words[rev_vocab[i]] =theta[i]
    print words
    D = {"words":words,"vocab":vocab,"vocabno":vocab_no,"rev_vocab":rev_vocab}
    savemodel("test-weights-sd.pickle.gz",D)

    # print len(test_pol)
    # print y_pred
    # lr.setup(theta,tfiles)
    # lr.grad_descent(tfiles,theta,vfiles)
    # print lr.predict(vfiles,theta)
   
