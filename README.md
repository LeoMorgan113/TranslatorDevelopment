# TranslatorDevelopment
![LM 113](https://user-images.githubusercontent.com/56256429/121577585-55b47f00-ca32-11eb-8824-9ced3f3a1f56.png)

The result of course work is the creation of imperative language general purpose programming __LM113__ written on Python. 

The explanatory note provides a detailed description of the grammar of the language, the structure of the lexical analyzer, translator and interpreter of the Polish inversion notation(POLIZ). 

This translator performs parsing, and if there are errors in the input text of the program creates a list of errors in the input program. 

The lexical analyzer uses state diagrams to parse the input text.

The translator supports _*arithmetic operations, work with negative ones numbers, conditional operator and loop operator,data input / output operators and exponential form of a real number.*_

Operators:
- __*for*__:
*for `ident`=`expression` to `expression` step `expression` do `list of operators` next*

- __*if*__:
*if `boolean expression` then `list of operators` fi*

Basic program example:
`program


a = 32-2/f


b = 0.4E+2


c = 900E-2


write(f)


for x=0 to 2.5 step 0.5 do


    write(x)
    
    
next


if a>=10 then


    write(a)
    
    
    if a==30 then
    
    
        a=a*2
	
	
	    write(a)
	    
	    
    fi
    
    
else


    b = b-10
    
    
    write(f)
    
    
fi


end`
