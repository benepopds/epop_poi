# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 10:40:48 2018

@author: epop
"""
b=[]
for i in range(0,3):
    print (i ,'is doing')
    if (i<1) :
        print(i,'is in if')
        continue
    if (i>=0) :
        a = 1
       
    
    try :
        a != b[1]
        
    except : 
        print(a)
        continue
    
    print (i ,'is done')
    


print (i ,'is going')