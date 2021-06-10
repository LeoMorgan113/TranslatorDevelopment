# TranslatorDevelopment
![LM 113](https://user-images.githubusercontent.com/56256429/121577585-55b47f00-ca32-11eb-8824-9ced3f3a1f56.png)

The aim of the course work is a software product written in the Python programming language in the JetBrains PyCharm environment.

The result of this course work is the creation of imperative language general purpose programming __LM113__. 

The explanatory note provides a detailed description of the grammar of the language, the structure of the lexical analyzer, translator and interpreter of the Polish inversion notation(POLIZ). 

This translator performs parsing, and if there are errors in the input text of the program creates a list of errors in the input program. 

The lexical analyzer uses state diagrams to parse the input text.

The translator supports _*arithmetic operations, work with negative ones numbers, conditional operator and loop operator,data input / output operators and exponential form of a real number.*_

- _*for*_ structure:
*for `ident`=`expression` to `expression` step `expression` do `list of operators` next*

- _*if*_ structure:
*if `boolean expression` then `list of operators` fi*
