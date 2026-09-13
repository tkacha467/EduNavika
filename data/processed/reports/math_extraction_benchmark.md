# Milestone 4.1.1: Mathematical Extraction Benchmark
Evaluating PDF extractors on 30 failed math pages to determine semantic preservation.

---
## Sample 1 [CHUNK_ID: chk_89b003ace9cd89f6]
**Document:** STD-10/Std-10_Maths_EnglishMedium.pdf | **Page:** 127

### 1. PyMuPDF (fitz)
```text
	
	

 	
0"'(/(
 A7
!9
!
2
2
2
1
2
1
(
)
(
) .
x
x
y
y
−
+
−
 7
!$
2
2 .
x
y
+
 7
!$&$
 )
 !  ,
 !      '  
1 2
2 1
1
2
2
1
1
2
1
2
,
m x
m x
m y
m y
m
m
m
m
⎛
⎞
+
+
⋅
⎜
⎟
+
+
⎝
⎠
 $&$7
!9
!
1
2
1
2
,
2
2
x
x
y
y
+
+
⎛
⎞
⎜
⎟
⎝
⎠

=8-=3
!
7$&$
)
!,
!''
C
1 2
2 1
1
2
m x
m x
m
m
+
+

C
1
2
2
1
1
2
m y
m y
m
m
+
+
%

7)'7,C'
"
7A),A),
$),
7)'7,C'
7
$&$),;
=3$
```

### 2. pypdf (Native)
```text
/G49/G49/G50 /G77/G65 /G84/G72/G69/G77/G65 /G84/G73/G67/G83
/G55/G46/G52 /G83/G117/G109/G109/G97/G114/G121
/G73/G110/G32/G116/G104/G105/G115/G32/G99/G104/G97/G112/G116/G101/G114/G44/G32/G121/G111/G117/G32/G104/G97/G118/G101/G32/G115/G116/G117/G100/G105/G101/G100/G32/G116/G104/G101/G32/G102/G111/G108/G108/G111/G119/G105/G110/G103/G32/G112/G111/G105/G110/G116/G115/G32/G58
/G49/G46/G84/G104/G101/G32/G100/G105/G115/G116/G97/G110/G99/G101/G32/G98/G101/G116/G119/G101/G101/G110/G32/G80/G40/G120/G49/G44/G32/G121/G49/G41/G32/G97/G110/G100/G32/G81/G40/G120/G50/G44/G32/G121/G50/G41/G32/G105/G115/G3222
21 2 1() ( ) .xx yy−+ −
/G50/G46/G84/G104/G101/G32/G100/G105/G115/G116/G97/G110/G99/G101/G32/G111/G102/G32/G97/G32/G112/G111/G105/G110/G116/G32/G80/G40/G120/G44/G32/G121/G41/G32/G102/G114/G111/G109/G32/G116/G104/G101/G32/G111/G114/G105/G103/G105/G110/G32/G105/G115/G3222 .xy +
/G51/G46/G84/G104/G101/G32/G99/G111/G111/G114/G100/G105/G110/G97/G116/G101/G115/G32/G111/G102/G32/G116/G104/G101/G32/G112/G111/G105/G110/G116/G32/G80/G40/G120/G44/G32/G121/G41/G32/G119/G104/G105/G99/G104/G32/G100/G105/G118/G105/G100/G101/G115/G32/G116/G104/G101/G32/G108/G105/G110/G101/G32/G115/G101/G103/G109/G101/G110/G116/G32/G106/G111/G105/G110/G105/G110/G103/G32/G116/G104/G101
/G112/G111/G105/G110/G116/G115/G32/G65/G40/G120/G49/G44/G32/G121/G49/G41/G32/G97/G110/G100/G32/G66/G40/G120/G50/G44/G32/G121/G50/G41/G32/G105/G110/G116/G101/G114/G110/G97/G108/G108/G121/G32/G105/G110/G32/G116/G104/G101/G32/G114/G97/G116/G105/G111/G32/G109/G49/G32/G58/G32/G109/G50/G32/G97/G114/G101
12 21 12 21
12 1 2
,mx m x my m y
mm m m
⎛⎞ ++ ⋅⎜⎟ ++⎝⎠
/G52/G46/G84/G104/G101/G32/G109/G105/G100/G45/G112/G111/G105/G110/G116/G32/G111/G102/G32/G116/G104/G101/G32/G108/G105/G110/G101/G32/G115/G101/G103/G109/G101/G110/G116/G32/G106/G111/G105/G110/G105/G110/G103/G32/G116/G104/G101/G32/G112/G111/G105/G110/G116/G115/G32/G80/G40/G120/G49/G44/G32/G121/G49/G41/G32/G97/G110/G100/G32/G81/G40/G120/G50/G44/G32/G121/G50/G41/G32/G105/G115
12 1 2 ,
22
xxy y++⎛⎞
⎜⎟⎝⎠
/G46
/G65/G32/G78/G79/G84/G69/G32/G84/G79/G32/G84/G72/G69/G32/G82/G69/G65/G68/G69/G82
/G83/G101/G99/G116/G105/G111/G110/G32/G55/G46/G51/G32/G100/G105/G115/G99/G117/G115/G115/G101/G115/G32/G116/G104/G101/G32/G83/G101/G99/G116/G105/G111/G110/G32/G70/G111/G114/G109/G117/G108/G97/G32/G102/G111/G114/G32/G116/G104/G101/G32/G99/G111/G111/G114/G100/G105/G110/G97/G116/G101/G115/G32/G40/G120/G44/G32/G121/G41/G32/G111/G102/G32/G97
/G112/G111/G105/G110/G116/G32/G80/G32/G119/G104/G105/G99/G104/G32/G32/G100/G105/G118/G105/G100/G101/G115/G32/G105/G110/G116/G101/G114/G110/G97/G108/G108/G121/G32/G116/G104/G101/G32/G108/G105/G110/G101/G32/G115/G101/G103/G109/G101/G110/G116/G32/G106/G111/G105/G110/G105/G110/G103/G32/G116/G104/G101/G32/G112/G111/G105/G110/G116/G115
/G65/G40/G120/G49/G44/G32/G121/G49/G41/G32/G97/G110/G100/G32/G66/G40/G120/G50/G44/G32/G121/G50/G41/G32/G105/G110/G32/G116/G104/G101/G32/G114/G97/G116/G105/G111/G32/G109/G49/G32/G58/G32/G109/G50/G32/G97/G115/G32/G102/G111/G108/G108/G111/G119/G115/G32/G58
/G120/G32/G61/G3212 21
12
mx m x
mm
+
+ /G32/G44/G121/G32/G61/G3212 21
12
my m y
mm
+
+
/G78/G111/G116/G101/G32/G116/G104/G97/G116/G44/G32/G104/G101/G114/G101/G44/G32/G80/G65/G32/G58/G32/G80/G66/G32/G61/G32/G109/G49/G32/G58/G32/G109/G50/G46
/G72/G111/G119/G101/G118/G101/G114/G44/G32/G105/G102/G32/G80/G32/G100/G111/G101/G115/G32/G110/G111/G116/G32/G108/G105/G101/G32/G98/G101/G116/G119/G101/G101/G110/G32/G65/G32/G97/G110/G100/G32/G66/G32/G98/G117/G116/G32/G108/G105/G101/G115/G32/G111/G110/G32/G116/G104/G101/G32/G108/G105/G110/G101/G32/G65/G66/G44
/G111/G117/G116/G115/G105/G100/G101/G32/G116/G104/G101/G32/G108/G105/G110/G101/G32/G115/G101/G103/G109/G101/G110/G116/G32/G65/G66/G44/G32/G97/G110/G100/G32/G80/G65/G32/G58/G32/G80/G66/G32/G61/G32/G109/G49/G32/G58/G32/G109/G50/G44/G32/G119/G101/G32/G115/G97/G121/G32/G116/G104/G97/G116/G32/G80/G32/G100/G105/G118/G105/G100/G101/G115
/G101/G120/G116/G101/G114/G110/G97/G108/G108/G121/G32/G116/G104/G101/G32/G108/G105/G110/G101/G32/G115/G101/G103/G109/G101/G110/G116/G32/G106/G111/G105/G110/G105/G110/G103/G32/G116/G104/G101/G32/G112/G111/G105/G110/G116/G115/G32/G65/G32/G97/G110/G100/G32/G66/G46/G32/G89/G111/G117/G32/G119/G105/G108/G108/G32/G115/G116/G117/G100/G121
/G83/G101/G99/G116/G105/G111/G110/G32/G70/G111/G114/G109/G117/G108/G97/G32/G102/G111/G114/G32/G115/G117/G99/G104/G32/G99/G97/G115/G101/G32/G105/G110/G32/G104/G105/G103/G104/G101/G114/G32/G99/G108/G97/G115/G115/G101/G115/G46
```

### 3. pypdfium2 (Current)
```text
	 	

 	
0"'(/(
 A7
!9
! 22
21 2 1 ( ) ( ). xx yy − +−
 7
!$ 22 xy + .
 7
!$&$
 )
 !  ,
 !      '  
12 21 1 2 21
12 1 2
, mx m x my m y
mm m m
⎛⎞ ++ ⋅ ⎜⎟ ⎝⎠ ++
 $&$7
!9
!
1 21 2 ,
22
⎛⎞ xxy y ++
⎜⎟ ⎝⎠ 

=8-=3
!
 7   $&$ 
)

!,
!''
C
12 21
12
mx m x
mm
+
+ 
 C
12 21
12
my m y
mm
+
+
%

7)'7,C'
"
 7   A) , A ),

$),
7)'7,C
'
7
$&$),;
=3$
```

---

## Sample 2 [CHUNK_ID: chk_09c682929b4337c7]
**Document:** STD-10/Std-10_Maths_EnglishMedium.pdf | **Page:** 26

### 1. PyMuPDF (fitz)
```text


	

$&


3
2
,
x
'&#
'&$#&%


#
##





≠4
67&'&"/
7$

$7$&'8$&"7&*/0&*2

$&'&"
&'&"7$5
4
74
&"




	


97&'&"7&%:9;
&%7&%&<'8&%=&"74
-

"7 "&'×"&"74
-&%74"74
&%">1
&'&"3
		

		
74
?	
>
 !
>7$#'
74
$#'74

7
3
2
−
⋅

>7#

7#
74


b
k
a
−
=
⋅
5
>#

(Constant term)
Coefficient of
b
a
x
−
−
=

/
>@
: !
>1
:

1
 	

	

?,>74A
>:/

	1
>
```

### 2. pypdf (Native)
```text
/G80/G79/G76 /G89/G78/G79/G77/G73/G65/G76/G83 /G49/G49
/G97/G32/G99/G117/G98/G105/G99/G32/G112/G111/G108/G121/G110/G111/G109/G105/G97/G108/G32/G97/G114/G101/G32/G50/G32/G150/G32/G120/G51/G44/G32/G120/G51/G44/G3232,x /G32/G51/G32/G150/G32/G120/G50/G32/G43/G32/G120/G51/G44/G32/G51/G120/G51/G32/G150/G32/G50/G120/G50/G32/G43/G32/G120/G32/G150/G32/G49/G46/G32/G73/G110/G32/G102/G97/G99/G116/G44/G32/G116/G104/G101/G32/G109/G111/G115/G116
/G103/G101/G110/G101/G114/G97/G108/G32/G102/G111/G114/G109/G32/G111/G102/G32/G97/G32/G99/G117/G98/G105/G99/G32/G112/G111/G108/G121/G110/G111/G109/G105/G97/G108/G32/G105/G115
/G97/G120/G51/G32/G43/G32/G98/G120/G50/G32/G43/G32/G99/G120/G32/G43/G32/G100/G44
/G119/G104/G101/G114/G101/G44/G32/G97/G44/G32/G98/G44/G32/G99/G44/G32/G100/G32/G97/G114/G101/G32/G114/G101/G97/G108/G32/G110/G117/G109/G98/G101/G114/G115/G32/G97/G110/G100/G32/G97/G32≠/G32/G48/G46
/G78/G111/G119/G32/G99/G111/G110/G115/G105/G100/G101/G114/G32/G116/G104/G101/G32/G112/G111/G108/G121/G110/G111/G109/G105/G97/G108/G32/G112/G40/G120/G41/G32/G61/G32/G120/G50/G32/G150/G32/G51/G120/G32/G150/G32/G52/G46/G32/G84/G104/G101/G110/G44/G32/G112/G117/G116/G116/G105/G110/G103/G32/G120/G32/G61/G32/G50/G32/G105/G110/G32/G116/G104/G101
/G112/G111/G108/G121/G110/G111/G109/G105/G97/G108/G44/G32/G119/G101/G32/G103/G101/G116/G32/G112/G40/G50/G41/G32/G61/G32/G50/G50/G32/G150/G32/G51/G32/G215/G32/G50/G32/G150/G32/G52/G32/G61/G32/G150/G32/G54/G46/G32/G84/G104/G101/G32/G118/G97/G108/G117/G101/G32/G145/G150/G32/G54/G146/G44/G32/G111/G98/G116/G97/G105/G110/G101/G100/G32/G98/G121/G32/G114/G101/G112/G108/G97/G99/G105/G110/G103
/G120/G32/G98/G121/G32/G50/G32/G105/G110/G32/G120/G50/G32/G150/G32/G51/G120/G32/G150/G32/G52/G44/G32/G105/G115/G32/G116/G104/G101/G32/G118/G97/G108/G117/G101/G32/G111/G102/G32/G120/G50/G32/G150/G32/G51/G120/G32/G150/G32/G52/G32/G97/G116/G32/G120/G32/G61/G32/G50/G46/G32/G83/G105/G109/G105/G108/G97/G114/G108/G121/G44/G32/G112/G40/G48/G41/G32/G105/G115/G32/G116/G104/G101/G32/G118/G97/G108/G117/G101/G32/G111/G102
/G112/G40/G120/G41/G32/G97/G116/G32/G120/G32/G61/G32/G48/G44/G32/G119/G104/G105/G99/G104/G32/G105/G115/G32/G150/G32/G52/G46
/G73/G102/G32/G112/G40/G120/G41/G32/G105/G115/G32/G97/G32/G112/G111/G108/G121/G110/G111/G109/G105/G97/G108/G32/G105/G110/G32/G120/G44/G32/G97/G110/G100/G32/G105/G102/G32/G107/G32/G105/G115/G32/G97/G110/G121/G32/G114/G101/G97/G108/G32/G110/G117/G109/G98/G101/G114/G44/G32/G116/G104/G101/G110/G32/G116/G104/G101/G32/G118/G97/G108/G117/G101/G32/G111/G98/G116/G97/G105/G110/G101/G100/G32/G98/G121
/G114/G101/G112/G108/G97/G99/G105/G110/G103/G32/G120/G32/G98/G121/G32/G107/G32/G105/G110/G32/G112/G40/G120/G41/G44/G32/G105/G115/G32/G99/G97/G108/G108/G101/G100/G32/G116/G104/G101/G32/G118/G97/G108/G117/G101/G32/G111/G102/G32/G112/G40/G120/G41/G32/G97/G116/G32/G120/G32/G61/G32/G107/G44/G32/G97/G110/G100/G32/G105/G115/G32/G100/G101/G110/G111/G116/G101/G100/G32/G98/G121/G32/G112/G40/G107/G41/G46
/G87/G104/G97/G116/G32/G105/G115/G32/G116/G104/G101/G32/G118/G97/G108/G117/G101/G32/G111/G102/G32/G112/G40/G120/G41/G32/G61/G32/G120/G50/G32/G150/G51/G120/G32/G150/G32/G52/G32/G97/G116/G32/G120/G32/G61/G32/G150/G49/G63/G32/G87/G101/G32/G104/G97/G118/G101/G32/G58
/G112/G40/G150/G49/G41/G32/G61/G32/G40/G150/G49/G41/G50/G32/G150/G123/G51/G32/G215/G32/G40/G150/G49/G41/G125/G32/G150/G32/G52/G32/G61/G32/G48
/G65/G108/G115/G111/G44/G32/G110/G111/G116/G101/G32/G116/G104/G97/G116/G112/G40/G52/G41/G32/G61/G52/G50/G32/G150/G32/G40/G51/G32×/G32/G52/G41/G32/G150/G32/G52/G32/G61/G32/G48/G46
/G65/G115/G32/G112/G40/G150/G49/G41/G32/G61/G32/G48/G32/G97/G110/G100/G32/G112/G40/G52/G41/G32/G61/G32/G48/G44/G32/G150/G49/G32/G97/G110/G100/G32/G52/G32/G97/G114/G101/G32/G99/G97/G108/G108/G101/G100/G32/G116/G104/G101/G32/G122/G101/G114/G111/G101/G115/G32/G111/G102/G32/G116/G104/G101/G32/G113/G117/G97/G100/G114/G97/G116/G105/G99
/G112/G111/G108/G121/G110/G111/G109/G105/G97/G108/G32/G120/G50/G32/G150/G32/G51/G120/G32/G150/G32/G52/G46/G32/G77/G111/G114/G101/G32/G103/G101/G110/G101/G114/G97/G108/G108/G121/G44/G32/G97/G32/G114/G101/G97/G108/G32/G110/G117/G109/G98/G101/G114/G32/G107/G32/G105/G115/G32/G115/G97/G105/G100/G32/G116/G111/G32/G98/G101/G32/G97/G32/G122/G101/G114/G111/G32/G111/G102/G32/G97
/G112/G111/G108/G121/G110/G111/G109/G105/G97/G108/G32/G112/G40/G120/G41/G44/G32/G105/G102/G32/G112/G40/G107/G41/G32/G61/G32/G48/G46
/G89/G111/G117/G32/G104/G97/G118/G101/G32/G97/G108/G114/G101/G97/G100/G121/G32/G115/G116/G117/G100/G105/G101/G100/G32/G105/G110/G32/G67/G108/G97/G115/G115/G32/G73/G88/G44/G32/G104/G111/G119/G32/G116/G111/G32/G102/G105/G110/G100/G32/G116/G104/G101/G32/G122/G101/G114/G111/G101/G115/G32/G111/G102/G32/G97/G32/G108/G105/G110/G101/G97/G114
/G112/G111/G108/G121/G110/G111/G109/G105/G97/G108/G46/G32/G70/G111/G114/G32/G101/G120/G97/G109/G112/G108/G101/G44/G32/G105/G102/G32/G107/G32/G105/G115/G32/G97/G32/G122/G101/G114/G111/G32/G111/G102/G32/G112/G40/G120/G41/G32/G61/G32/G50/G120/G32/G43/G32/G51/G44/G32/G116/G104/G101/G110/G32/G112/G40/G107/G41/G32/G61/G32/G48/G32/G103/G105/G118/G101/G115/G32/G117/G115
/G50/G107/G32/G43/G32/G51/G32/G61/G32/G48/G44/G32/G105/G46/G101/G46/G44/G32/G107/G32/G61/G323
2−⋅
/G73/G110/G32/G103/G101/G110/G101/G114/G97/G108/G44/G32/G105/G102/G32/G107/G32/G105/G115/G32/G97/G32/G122/G101/G114/G111/G32/G111/G102/G32/G112/G40/G120/G41/G32/G61/G32/G97/G120/G32/G43/G32/G98/G44/G32/G116/G104/G101/G110/G32/G112/G40/G107/G41/G32/G61/G32/G97/G107/G32/G43/G32/G98/G32/G61/G32/G48/G44/G32/G105/G46/G101/G46/G44/G32bk a
−=⋅
/G83/G111/G44/G32/G116/G104/G101/G32/G122/G101/G114/G111/G32/G111/G102/G32/G116/G104/G101/G32/G108/G105/G110/G101/G97/G114/G32/G112/G111/G108/G121/G110/G111/G109/G105/G97/G108/G32/G97/G120/G32/G43/G32/G98/G32/G105/G115/G32(Constant term)
Coefficient of
b
ax
−− = /G46
/G84/G104/G117/G115/G44/G32/G116/G104/G101/G32/G122/G101/G114/G111/G32/G111/G102/G32/G97/G32/G108/G105/G110/G101/G97/G114/G32/G112/G111/G108/G121/G110/G111/G109/G105/G97/G108/G32/G105/G115/G32/G114/G101/G108/G97/G116/G101/G100/G32/G116/G111/G32/G105/G116/G115/G32/G99/G111/G101/G102/G102/G105/G99/G105/G101/G110/G116/G115/G46/G32/G68/G111/G101/G115/G32/G116/G104/G105/G115
/G104/G97/G112/G112/G101/G110/G32/G105/G110/G32/G116/G104/G101/G32/G99/G97/G115/G101/G32/G111/G102/G32/G111/G116/G104/G101/G114/G32/G112/G111/G108/G121/G110/G111/G109/G105/G97/G108/G115/G32/G116/G111/G111/G63/G32/G70/G111/G114/G32/G101/G120/G97/G109/G112/G108/G101/G44/G32/G97/G114/G101/G32/G116/G104/G101/G32/G122/G101/G114/G111/G101/G115/G32/G111/G102/G32/G97/G32/G113/G117/G97/G100/G114/G97/G116/G105/G99
/G112/G111/G108/G121/G110/G111/G109/G105/G97/G108/G32/G97/G108/G115/G111/G32/G114/G101/G108/G97/G116/G101/G100/G32/G116/G111/G32/G105/G116/G115/G32/G99/G111/G101/G102/G102/G105/G99/G105/G101/G110/G116/G115/G63
/G73/G110/G32/G116/G104/G105/G115/G32/G99/G104/G97/G112/G116/G101/G114/G44/G32/G119/G101/G32/G119/G105/G108/G108/G32/G116/G114/G121/G32/G116/G111/G32/G97/G110/G115/G119/G101/G114/G32/G116/G104/G101/G115/G101/G32/G113/G117/G101/G115/G116/G105/G111/G110/G115/G46
/G50/G46/G50 /G71/G101/G111/G109/G101/G116/G114/G105/G99/G97/G108/G32/G77/G101/G97/G110/G105/G110/G103/G32/G111/G102/G32/G116/G104/G101/G32/G90/G101/G114/G111/G101/G115/G32/G111/G102/G32/G97/G32/G80/G111/G108/G121/G110/G111/G109/G105/G97/G108
/G89/G111/G117/G32/G107/G110/G111/G119/G32/G116/G104/G97/G116/G32/G97/G32/G114/G101/G97/G108/G32/G110/G117/G109/G98/G101/G114/G32/G107/G32/G105/G115/G32/G97/G32/G122/G101/G114/G111/G32/G111/G102/G32/G116/G104/G101/G32/G112/G111/G108/G121/G110/G111/G109/G105/G97/G108/G32/G112/G40/G120/G41/G32/G105/G102/G32/G112/G40/G107/G41/G32/G61/G32/G48/G46/G32/G66/G117/G116/G32/G119/G104/G121
/G97/G114/G101/G32/G116/G104/G101/G32/G122/G101/G114/G111/G101/G115/G32/G111/G102/G32/G97/G32/G112/G111/G108/G121/G110/G111/G109/G105/G97/G108/G32/G115/G111/G32/G105/G109/G112/G111/G114/G116/G97/G110/G116/G63/G32/G84/G111/G32/G97/G110/G115/G119/G101/G114/G32/G116/G104/G105/G115/G44/G32/G102/G105/G114/G115/G116/G32/G119/G101/G32/G119/G105/G108/G108/G32/G115/G101/G101/G32/G116/G104/G101
/G103/G101/G111/G109/G101/G116/G114/G105/G99/G97/G108/G32/G114/G101/G112/G114/G101/G115/G101/G110/G116/G97/G116/G105/G111/G110/G115/G32/G111/G102/G32/G108/G105/G110/G101/G97/G114/G32/G97/G110/G100/G32/G113/G117/G97/G100/G114/G97/G116/G105/G99/G32/G112/G111/G108/G121/G110/G111/G109/G105/G97/G108/G115/G32/G97/G110/G100/G32/G116/G104/G101/G32/G103/G101/G111/G109/G101/G116/G114/G105/G99/G97/G108
/G109/G101/G97/G110/G105/G110/G103/G32/G111/G102/G32/G116/G104/G101/G105/G114/G32/G122/G101/G114/G111/G101/G115/G46
```

### 3. pypdfium2 (Current)
```text


	 
$&

 3 2, x '&#
'&$#&%



#
##






 ≠4
6 7
 & ' & "/
  7 $

$7$&'8$&"7&*/0&*2

$&'&"
&'&"7$5
4
74
&"




	


97&'&"7&%:9;
&%7&%&<'8&%=&"74
-
 "7 "&'×"&"74
-&% 7 4 " 7 4
 &%  "   >  1

&'&"3
 		

		
74
?    	
   >  
 !
>7$#'
74
$#'74

7
3
2
−⋅

>7#

7#
74


b k
a
− =⋅
5
>#
 (Constant term)
Coefficient of
b
ax
−− = 
/
>   @
: !
>1
:

1
 	

	

?,>74A
>:/
 
	1
>
```

---

## Sample 3 [CHUNK_ID: chk_a656d065a98ab396]
**Document:** STD-10/Std-10_Science_English Medium.pdf | **Page:** 38

### 1. PyMuPDF (fitz)
```text
Acids, Bases and Salts
25
2.3 HOW STRONG ARE ACID OR BASE SOLUTIONS?
2.3 HOW STRONG ARE ACID OR BASE SOLUTIONS?
2.3 HOW STRONG ARE ACID OR BASE SOLUTIONS?
2.3 HOW STRONG ARE ACID OR BASE SOLUTIONS?
2.3 HOW STRONG ARE ACID OR BASE SOLUTIONS?
We know how acid-base indicators can be used to distinguish between
an acid and a base. We have also learnt in the previous section about
dilution and decrease in concentration of H+ or OH– ions in solutions.
Can we quantitatively find the amount of these ions present in a solution?
Can we judge how strong a given acid or base is?
We can do this by making use of a universal indicator, which is a
mixture of several indicators. The universal indicator shows different
colours at different concentrations of hydrogen ions in a solution.
A scale for measuring hydrogen ion concentration in a solution, called
pH scale has been developed. The p in pH stands for ‘potenz’ in German,
meaning power. On the pH scale we can measure pH generally from
0 (very acidic) to 14 (very alkaline). pH should be thought of simply as a
number which indicates the acidic or basic nature of a solution. Higher
the hydronium ion concentration, lower is the pH value.
The pH of a neutral solution is 7. Values less than 7 on the pH scale
represent an acidic solution. As the pH value increases from 7 to 14, it
represents an increase in OH– ion concentration in the solution, that is,
increase in the strength of alkali (Fig. 2.6). Generally paper impregnated
with the universal indicator is used for measuring pH.
Q
U
E
S
T
I
O
N
S
?
1.
Why do HCl, HNO3, etc., show acidic characters in aqueous solutions
while solutions of compounds like alcohol and glucose do not show acidic
character?
2.
Why does an aqueous solution of an acid conduct electricity?
3.
Why does dry HCl gas not change the colour of the dry litmus paper?
4.
While diluting an acid, why is it recommended that the acid should be
added to water and not water to the acid?
5.
How is the concentration of hydronium ions (H3O+) affected when a
solution of an acid is diluted?
6.
How is the concentration of hydroxide ions (OH
–) affected when excess
base is dissolved in a solution of sodium hydroxide?
Figure 2.6
Figure 2.6
Figure 2.6
Figure 2.6
Figure 2.6 Variation of pH with the change in concentration of  H+(aq) and OH–(aq) ions
```

### 2. pypdf (Native)
```text
Acids, Bases and Salts 25
2.3 HOW STRONG ARE ACID OR BASE SOLUTIONS?2.3 HOW STRONG ARE ACID OR BASE SOLUTIONS?2.3 HOW STRONG ARE ACID OR BASE SOLUTIONS?2.3 HOW STRONG ARE ACID OR BASE SOLUTIONS?2.3 HOW STRONG ARE ACID OR BASE SOLUTIONS?
We know how acid-base indicators can be used to distinguish between
an acid and a base. We have also learnt in the pr
evious section about
dilution and decrease in concentration of H+ or OH– ions in solutions.
Can we quantitatively find the amount of these ions present in a solution?
Can we judge how strong a given acid or base is?
We can do this by making use of a universal indicator, which is a
mixture of several indicators. The universal indicator shows different
colours at different concentrations of hydrogen ions in a solution.
A scale for measuring hydrogen ion concentration in a solution, called
pH scale has been developed. The p in pH stands for ‘potenz’ in German,
meaning power. On the pH scale we can measur e pH generally from
0 (very acidic) to 14 (very alkaline). pH should be thought of simply as a
number which indicates the acidic or basic nature of a solution. Higher
the hydronium ion concentration, lower is the pH value.
The pH of a neutral solution is 7. Values less than 7 on the pH scale
represent an acidic solution. As the pH value increases from 7 to 14, it
represents an increase in OH– ion concentration in the solution, that is,
increase in the strength of alkali (Fig. 2.6). Generally paper impregnated
with the universal indicator is used for measuring pH.
QUESTIONS
?
1. Why do HCl, HNO 3, etc., show acidic characters in aqueous solutions
while solutions of compounds like alcohol and glucose do not show acidic
character?
2. Why does an aqueous solution of an acid conduct electricity?
3. Why does dry HCl gas not change the colour of the dry litmus paper?
4. While diluting an acid, why is it recommended that the acid should be
added to water and not water to the acid?
5. How is the concentration of hydronium ions (H 3O+) affected when a
solution of an acid is diluted?
6. How is the concentration of hydroxide ions (O H
–
) affected when excess
base is dissolved in a solution of sodium hydroxide?
Figure 2.6Figure 2.6Figure 2.6Figure 2.6Figure 2.6  Variation of pH with the change in concentration of  H+(aq)  and OH–(aq) ions
```

### 3. pypdfium2 (Current)
```text
Acids, Bases and Salts 25
2.3 HOW STRONG ARE ACID OR BASE SOLUTIONS?
We know how acid-base indicators can be used to distinguish between
an acid and a base. We have also learnt in the previous section about
dilution and decrease in concentration of H+ or OH– ions in solutions.
Can we quantitatively find the amount of these ions present in a solution?
Can we judge how strong a given acid or base is?
We can do this by making use of a universal indicator, which is a
mixture of several indicators. The universal indicator shows different
colours at different concentrations of hydrogen ions in a solution.
A scale for measuring hydrogen ion concentration in a solution, called
pH scale has been developed. The p in pH stands for ‘potenz’ in German,
meaning power. On the pH scale we can measure pH generally from
0 (very acidic) to 14 (very alkaline). pH should be thought of simply as a
number which indicates the acidic or basic nature of a solution. Higher
the hydronium ion concentration, lower is the pH value.
The pH of a neutral solution is 7. Values less than 7 on the pH scale
represent an acidic solution. As the pH value increases from 7 to 14, it
represents an increase in OH– ion concentration in the solution, that is,
increase in the strength of alkali (Fig. 2.6). Generally paper impregnated
with the universal indicator is used for measuring pH.
QUESTIONS
?
1. Why do HCl, HNO3, etc., show acidic characters in aqueous solutions
while solutions of compounds like alcohol and glucose do not show acidic
character?
2. Why does an aqueous solution of an acid conduct electricity?
3. Why does dry HCl gas not change the colour of the dry litmus paper?
4. While diluting an acid, why is it recommended that the acid should be
added to water and not water to the acid?
5. How is the concentration of hydronium ions (H3O+) affected when a
solution of an acid is diluted?
6. How is the concentration of hydroxide ions (OH
–
) affected when excess
base is dissolved in a solution of sodium hydroxide?
Figure 2.6 Variation of pH with the change in concentration of H+
(aq) and OH–
(aq) ions
```

---

## Sample 4 [CHUNK_ID: chk_b6e94e466a7dd168]
**Document:** STD-10/Std-10_Science_English Medium.pdf | **Page:** 16

### 1. PyMuPDF (fitz)
```text
Chemical Reactions and Equations
3
1.1.1 Writing a Chemical Equation
Is there any other shorter way for representing chemical equations?
Chemical equations can be made more concise and useful if we use
chemical formulae instead of words. A chemical equation represents a
chemical reaction. If you recall formulae of magnesium, oxygen and
magnesium oxide, the above word-equation can be written as –
Mg + O2  →  MgO
(1.2)
Count and compare the number of atoms of each element on the
LHS and RHS of the arrow. Is the number of atoms of each element the
same on both the sides? If yes, then the equation is balanced. If not,
then the equation is unbalanced because the mass is not the same on
both sides of the equation. Such a chemical equation is a skeletal
chemical equation for a reaction. Equation (1.2) is a skeletal chemical
equation for the burning of magnesium in air.
1.1.2 Balanced Chemical Equations
Recall the law of conservation of mass that you studied in Class IX; mass
can neither be created nor destroyed in a chemical reaction. That is, the
total mass of the elements present in the products of a chemical reaction
has to be equal to the total mass of the elements present in the reactants.
In other words, the number of atoms of each element remains the
same, before and after a chemical reaction. Hence, we need to balance a
skeletal chemical equation. Is the chemical Eq. (1.2) balanced? Let us
learn about balancing a chemical equation step by step.
The word-equation for Activity 1.3 may be represented as –
Zinc + Sulphuric acid  →  Zinc sulphate + Hydrogen
The above word-equation may be represented by the following
chemical equation –
Zn + H2SO4 → ZnSO4 + H2
(1.3)
Let us examine the number of atoms of different elements on both
sides of the arrow.
Element
Number of atoms in
Number of atoms
reactants (LHS)
in products (RHS)
Zn
1
1
H
2
2
S
1
1
O
4
4
As the number of atoms of each element is the same on both sides of
the arrow, Eq. (1.3) is a balanced chemical equation.
Let us try to balance the following chemical equation –
Fe + H2O → Fe3O4 + H2
(1.4)
```

### 2. pypdf (Native)
```text
Chemical Reactions and Equations 3
1.1.1 Writing a Chemical Equation
Is there any other shorter way for representing chemical equations?
Chemical equations can be made more concise and useful if we use
chemical formulae instead of words. A chemical equation represents a
chemical reaction. If you recall formulae of magnesium, oxygen and
magnesium oxide, the above word-equation can be written as –
Mg + O2  →  MgO (1.2)
Count and compare the number of atoms of each element on the
LHS and RHS of the arrow. Is the number of atoms of each element the
same on both the sides? If yes, then the equation is balanced. If not,
then the equation is unbalanced because the mass is not the same on
both sides of the equation. Such a chemical equation is a skeletal
chemical equation for a reaction. Equation (1.2) is a skeletal chemical
equation for the burning of magnesium in air.
1.1.2 Balanced Chemical Equations
Recall the law of conservation of mass that you studied in Class IX; mass
can neither be created nor destroyed in a chemical reaction. That is, the
total mass of the elements present in the products of a chemical reaction
has to be equal to the total mass of the elements present in the reactants.
In other words, the number of atoms of each element remains the
same, before and after a chemical reaction. Hence, we need to balance a
skeletal chemical equation. Is the chemical Eq. (1.2) balanced? Let us
learn about balancing a chemical equation step by step.
The word-equation for Activity 1.3 may be represented as –
Zinc + Sulphuric acid  →  Zinc sulphate + Hydrogen
The above word-equation may be represented by the following
chemical equation –
Zn + H2SO4 → ZnSO4 + H2 (1.3)
Let us examine the number of atoms of different elements on both
sides of the arrow.
Element Number of atoms in Number of atoms
reactants (LHS) in products (RHS)
Zn 1 1
H 2 2
S 1 1
O 4 4
As the number of atoms of each element is the same on both sides of
the arrow, Eq. (1.3) is a balanced chemical equation.
Let us try to balance the following chemical equation –
Fe + H2O → Fe3O4 + H2 (1.4)
```

### 3. pypdfium2 (Current)
```text
Chemical Reactions and Equations 3
1.1.1 Writing a Chemical Equation
Is there any other shorter way for representing chemical equations?
Chemical equations can be made more concise and useful if we use
chemical formulae instead of words. A chemical equation represents a
chemical reaction. If you recall formulae of magnesium, oxygen and
magnesium oxide, the above word-equation can be written as –
Mg + O2 → MgO (1.2)
Count and compare the number of atoms of each element on the
LHS and RHS of the arrow. Is the number of atoms of each element the
same on both the sides? If yes, then the equation is balanced. If not,
then the equation is unbalanced because the mass is not the same on
both sides of the equation. Such a chemical equation is a skeletal
chemical equation for a reaction. Equation (1.2) is a skeletal chemical
equation for the burning of magnesium in air.
1.1.2 Balanced Chemical Equations
Recall the law of conservation of mass that you studied in Class IX; mass
can neither be created nor destroyed in a chemical reaction. That is, the
total mass of the elements present in the products of a chemical reaction
has to be equal to the total mass of the elements present in the reactants.
In other words, the number of atoms of each element remains the
same, before and after a chemical reaction. Hence, we need to balance a
skeletal chemical equation. Is the chemical Eq. (1.2) balanced? Let us
learn about balancing a chemical equation step by step.
The word-equation for Activity 1.3 may be represented as –
Zinc + Sulphuric acid → Zinc sulphate + Hydrogen
The above word-equation may be represented by the following
chemical equation –
Zn + H2SO4 → ZnSO4 + H2(1.3)
Let us examine the number of atoms of different elements on both
sides of the arrow.
Element Number of atoms in Number of atoms
reactants (LHS) in products (RHS)
Zn 1 1
H 2 2
S 1 1
O 4 4
As the number of atoms of each element is the same on both sides of
the arrow, Eq. (1.3) is a balanced chemical equation.
Let us try to balance the following chemical equation –
Fe + H2O → Fe3O4 + H2(1.4)
```

---

## Sample 5 [CHUNK_ID: chk_aa66ec8e0c256b13]
**Document:** STD-10/Std-10_Maths_EnglishMedium.pdf | **Page:** 258

### 1. PyMuPDF (fitz)
```text
	
		

 
 

	
					

				
		 

			
	
				!
 "

	
			
				

	#		$	
 

'

(




6
6
7
7
8


?

7
@
6
?
78
A


?A

88
6
677
7
7@@
8


A?@

A@
	%
		%$$&



```

### 2. pypdf (Native)
```text
/G77/G65 /G84/G72/G69/G77/G65 /G84/G73/G67/G65/G76/G32/G77/G79/G68/G69/G76/G76/G73/G78/G71 /G50/G52/G51
/G69/G88/G69/G82/G67/G73/G83/G69 /G65/G50/G46/G49
/G49/G46/G67/G111/G110/G115/G105/G100/G101/G114/G32/G116/G104/G101/G32/G102/G111/G108/G108/G111/G119/G105/G110/G103/G32/G115/G105/G116/G117/G97/G116/G105/G111/G110/G46
/G65/G32/G112/G114/G111/G98/G108/G101/G109/G32/G100/G97/G116/G105/G110/G103/G32/G98/G97/G99/G107/G32/G116/G111/G32/G116/G104/G101/G32/G101/G97/G114/G108/G121/G32/G49/G51/G116/G104/G32/G99/G101/G110/G116/G117/G114/G121/G44/G32/G112/G111/G115/G101/G100/G32/G98/G121/G32/G76/G101/G111/G110/G97/G114/G100/G111/G32/G70/G105/G98/G111/G110/G97/G99/G99/G105/G32/G97/G115/G107/G115
/G104/G111/G119/G32/G109/G97/G110/G121/G32/G114/G97/G98/G98/G105/G116/G115/G32/G121/G111/G117/G32/G119/G111/G117/G108/G100/G32/G104/G97/G118/G101/G32/G105/G102/G32/G121/G111/G117/G32/G115/G116/G97/G114/G116/G101/G100/G32/G119/G105/G116/G104/G32/G106/G117/G115/G116/G32/G116/G119/G111/G32/G97/G110/G100/G32/G108/G101/G116/G32/G116/G104/G101/G109/G32/G114/G101/G112/G114/G111/G100/G117/G99/G101/G46
/G65/G115/G115/G117/G109/G101/G32/G116/G104/G97/G116/G32/G97/G32/G112/G97/G105/G114/G32/G111/G102/G32/G114/G97/G98/G98/G105/G116/G115/G32/G112/G114/G111/G100/G117/G99/G101/G115/G32/G97/G32/G112/G97/G105/G114/G32/G111/G102/G32/G111/G102/G102/G115/G112/G114/G105/G110/G103/G32/G101/G97/G99/G104/G32/G109/G111/G110/G116/G104/G32/G97/G110/G100/G32/G116/G104/G97/G116/G32/G101/G97/G99/G104
/G112/G97/G105/G114/G32/G111/G102/G32/G114/G97/G98/G98/G105/G116/G115/G32/G112/G114/G111/G100/G117/G99/G101/G115/G32/G116/G104/G101/G105/G114/G32/G102/G105/G114/G115/G116/G32/G111/G102/G102/G115/G112/G114/G105/G110/G103/G32/G97/G116/G32/G116/G104/G101/G32/G97/G103/G101/G32/G111/G102/G32/G50/G32/G109/G111/G110/G116/G104/G115/G46/G32/G77/G111/G110/G116/G104/G32/G98/G121/G32/G109/G111/G110/G116/G104
/G116/G104/G101/G32/G110/G117/G109/G98/G101/G114/G32/G111/G102/G32/G112/G97/G105/G114/G115/G32/G111/G102/G32/G114/G97/G98/G98/G105/G116/G115/G32/G105/G115/G32/G103/G105/G118/G101/G110/G32/G98/G121/G32/G116/G104/G101/G32/G115/G117/G109/G32/G111/G102/G32/G116/G104/G101/G32/G114/G97/G98/G98/G105/G116/G115/G32/G105/G110/G32/G116/G104/G101/G32/G116/G119/G111/G32/G112/G114/G101/G99/G101/G100/G105/G110/G103
/G109/G111/G110/G116/G104/G115/G44/G32/G101/G120/G99/G101/G112/G116/G32/G102/G111/G114/G32/G116/G104/G101/G32/G48/G116/G104/G32/G97/G110/G100/G32/G116/G104/G101/G32/G49/G115/G116/G32/G109/G111/G110/G116/G104/G115/G46
/G77/G111/G110/G116/G104/G80/G97/G105/G114/G115/G32/G111/G102/G32/G82/G97/G98/G98/G105/G116/G115
/G48/G49
/G49/G49
/G50/G50
/G51/G51
/G52/G53
/G53/G56
/G54/G49 /G51
/G55/G50 /G49
/G56/G51 /G52
/G57/G53 /G53
/G49/G48 /G56/G57
/G49/G49 /G49/G52/G52
/G49/G50 /G50/G51/G51
/G49/G51 /G51/G55/G55
/G49/G52 /G54/G49/G48
/G49/G53 /G57/G56/G55
/G49/G54 /G49/G53/G57/G55
/G65/G102/G116/G101/G114/G32/G106/G117/G115/G116/G32/G49/G54/G32/G109/G111/G110/G116/G104/G115/G44/G32/G121/G111/G117/G32/G104/G97/G118/G101/G32/G110/G101/G97/G114/G108/G121/G32/G49/G54/G48/G48/G32/G112/G97/G105/G114/G115/G32/G111/G102/G32/G114/G97/G98/G98/G105/G116/G115/G33
/G67/G108/G101/G97/G114/G108/G121/G32/G115/G116/G97/G116/G101/G32/G116/G104/G101/G32/G112/G114/G111/G98/G108/G101/G109/G32/G97/G110/G100/G32/G116/G104/G101/G32/G100/G105/G102/G102/G101/G114/G101/G110/G116/G32/G115/G116/G97/G103/G101/G115/G32/G111/G102/G32/G109/G97/G116/G104/G101/G109/G97/G116/G105/G99/G97/G108/G32/G109/G111/G100/G101/G108/G108/G105/G110/G103/G32/G105/G110/G32/G116/G104/G105/G115
/G115/G105/G116/G117/G97/G116/G105/G111/G110/G46
```

### 3. pypdfium2 (Current)
```text
	
		 
 
 

	
					

				
		 

			
	
				!
 "

	
			
				

	#		$	
 
 '

(


66
77
8
?
7
@6
?78
A
 ?A
 88
6 677
7 7@@
8 
 A?@
 A@
	%
		%$$&



```

---

## Sample 6 [CHUNK_ID: chk_1ce422ad424b13de]
**Document:** STD-10/Std-10_Maths_EnglishMedium.pdf | **Page:** 160

### 1. PyMuPDF (fitz)
```text

	

	
			*			

	
			#$%+,				
"
	
		*
		
*
		
				
			*
'
		*
			
			
		*	
	"	-
				
"	*	*	
			
			
'
		
*"		
				
	

*
				

 	

'		

	*	
				
	
	
	
	
	
!	
		
						
	
		
&
!		
	()	
	
	"			
*
	"	
	*			()"				

	

	.
		#$%/0
'


			
	
	
		  
 	'	
*
		
	
				*
		

(′)′()!


		


			1	*
"
			

()
	
				
*2
22	*"
		

	
			
	

3	*"	*
	"
		
	
()
	

	
(′)′	
* 		()	
	*	
					4	*	
		
(′)′()(		
(′′)′′
	
"-!	2*	
				
	*	
	
		
&
		

		
	

	


		

	
 
 
	


	


		
	

	
 		
	!
"
#$#%&#
```

### 2. pypdf (Native)
```text
/G67/G73/G82/G67/G76/G69/G83 /G49/G52/G53
/G89/G111/G117/G32/G109/G105/G103/G104/G116/G32/G104/G97/G118/G101/G32/G115/G101/G101/G110/G32/G97/G32/G112/G117/G108/G108/G101/G121/G32/G102/G105/G116/G116/G101/G100/G32/G111/G118/G101/G114/G32/G97/G32/G119/G101/G108/G108/G32/G119/G104/G105/G99/G104/G32/G105/G115/G32/G117/G115/G101/G100
/G105/G110/G32/G116/G97/G107/G105/G110/G103/G32/G111/G117/G116/G32/G119/G97/G116/G101/G114/G32/G102/G114/G111/G109/G32/G116/G104/G101/G32/G119/G101/G108/G108/G46/G32/G76/G111/G111/G107/G32/G97/G116/G32/G70/G105/G103/G46/G32/G49/G48/G46/G50/G46/G32/G72/G101/G114/G101/G32/G116/G104/G101/G32/G114/G111/G112/G101
/G111/G110/G32/G98/G111/G116/G104/G32/G115/G105/G100/G101/G115/G32/G111/G102/G32/G116/G104/G101/G32/G112/G117/G108/G108/G101/G121/G44/G32/G105/G102/G32/G99/G111/G110/G115/G105/G100/G101/G114/G101/G100/G32/G97/G115/G32/G97/G32/G114/G97/G121/G44/G32/G105/G115/G32/G108/G105/G107/G101/G32/G97/G32/G116/G97/G110/G103/G101/G110/G116
/G116/G111/G32/G116/G104/G101/G32/G99/G105/G114/G99/G108/G101/G32/G114/G101/G112/G114/G101/G115/G101/G110/G116/G105/G110/G103/G32/G116/G104/G101/G32/G112/G117/G108/G108/G101/G121/G46
/G73/G115/G32/G116/G104/G101/G114/G101/G32/G97/G110/G121/G32/G112/G111/G115/G105/G116/G105/G111/G110/G32/G111/G102/G32/G116/G104/G101/G32/G108/G105/G110/G101/G32/G119/G105/G116/G104/G32/G114/G101/G115/G112/G101/G99/G116/G32/G116/G111/G32/G116/G104/G101/G32/G99/G105/G114/G99/G108/G101
/G111/G116/G104/G101/G114/G32/G116/G104/G97/G110/G32/G116/G104/G101/G32/G116/G121/G112/G101/G115/G32/G103/G105/G118/G101/G110/G32/G97/G98/G111/G118/G101/G63/G32/G89/G111/G117/G32/G99/G97/G110/G32/G115/G101/G101/G32/G116/G104/G97/G116/G32/G116/G104/G101/G114/G101/G32/G99/G97/G110/G110/G111/G116
/G98/G101/G32/G97/G110/G121/G32/G111/G116/G104/G101/G114/G32/G116/G121/G112/G101/G32/G111/G102/G32/G112/G111/G115/G105/G116/G105/G111/G110/G32/G111/G102/G32/G116/G104/G101/G32/G108/G105/G110/G101/G32/G119/G105/G116/G104/G32/G114/G101/G115/G112/G101/G99/G116/G32/G32/G116/G111/G32/G116/G104/G101/G32/G99/G105/G114/G99/G108/G101/G46
/G73/G110/G32/G116/G104/G105/G115/G32/G99/G104/G97/G112/G116/G101/G114/G44/G32/G119/G101/G32/G119/G105/G108/G108/G32/G115/G116/G117/G100/G121/G32/G97/G98/G111/G117/G116/G32/G116/G104/G101/G32/G101/G120/G105/G115/G116/G101/G110/G99/G101/G32/G111/G102/G32/G116/G104/G101/G32/G116/G97/G110/G103/G101/G110/G116/G115
/G116/G111/G32/G97/G32/G99/G105/G114/G99/G108/G101/G32/G97/G110/G100/G32/G97/G108/G115/G111/G32/G115/G116/G117/G100/G121/G32/G115/G111/G109/G101/G32/G111/G102/G32/G116/G104/G101/G105/G114/G32/G112/G114/G111/G112/G101/G114/G116/G105/G101/G115/G46
/G49/G48/G46/G50 /G84/G97/G110/G103/G101/G110/G116/G32/G116/G111/G32/G97/G32/G67/G105/G114/G99/G108/G101
/G73/G110/G32/G116/G104/G101/G32/G112/G114/G101/G118/G105/G111/G117/G115/G32/G115/G101/G99/G116/G105/G111/G110/G44/G32/G121/G111/G117/G32/G104/G97/G118/G101/G32/G115/G101/G101/G110/G32/G116/G104/G97/G116/G32/G97/G32/G116/G97/G110/G103/G101/G110/G116/G42/G32/G116/G111/G32/G97/G32/G99/G105/G114/G99/G108/G101/G32/G105/G115/G32/G97/G32/G108/G105/G110/G101/G32/G116/G104/G97/G116
/G105/G110/G116/G101/G114/G115/G101/G99/G116/G115/G32/G116/G104/G101/G32/G99/G105/G114/G99/G108/G101/G32/G97/G116/G32/G111/G110/G108/G121/G32/G111/G110/G101/G32/G112/G111/G105/G110/G116/G46
/G84/G111/G32/G117/G110/G100/G101/G114/G115/G116/G97/G110/G100/G32/G116/G104/G101/G32/G101/G120/G105/G115/G116/G101/G110/G99/G101/G32/G111/G102/G32/G116/G104/G101/G32/G116/G97/G110/G103/G101/G110/G116/G32/G116/G111/G32/G97/G32/G99/G105/G114/G99/G108/G101/G32/G97/G116/G32/G97/G32/G112/G111/G105/G110/G116/G44/G32/G108/G101/G116/G32/G117/G115/G32/G112/G101/G114/G102/G111/G114/G109
/G116/G104/G101/G32/G102/G111/G108/G108/G111/G119/G105/G110/G103/G32/G97/G99/G116/G105/G118/G105/G116/G105/G101/G115/G58
/G65/G99/G116/G105/G118/G105/G116/G121/G32/G49/G32/G58/G32/G84/G97/G107/G101/G32/G97/G32/G99/G105/G114/G99/G117/G108/G97/G114/G32/G119/G105/G114/G101/G32/G97/G110/G100/G32/G97/G116/G116/G97/G99/G104/G32/G97/G32/G115/G116/G114/G97/G105/G103/G104/G116/G32/G119/G105/G114/G101/G32/G65/G66/G32/G97/G116/G32/G97/G32/G112/G111/G105/G110/G116/G32/G80/G32/G111/G102/G32/G116/G104/G101
/G99/G105/G114/G99/G117/G108/G97/G114/G32
/G119/G105/G114/G101/G32/G115/G111/G32/G116/G104/G97/G116/G32/G105/G116/G32/G99/G97/G110/G32/G114/G111/G116/G97/G116/G101/G32/G97/G98/G111/G117/G116/G32/G116/G104/G101/G32/G112/G111/G105/G110/G116/G32/G80/G32/G105/G110/G32/G97/G32/G112/G108/G97/G110/G101/G46/G32/G80/G117/G116/G32/G116/G104/G101/G32/G115/G121/G115/G116/G101/G109/G32/G111/G110/G32/G97/G32/G116/G97/G98/G108/G101
/G97/G110/G100/G32/G103/G101/G110/G116/G108/G121/G32/G114/G111/G116/G97/G116/G101/G32/G116/G104/G101/G32/G119/G105/G114/G101/G32/G65/G66/G32/G97/G98/G111/G117/G116/G32/G116/G104/G101/G32/G112/G111/G105/G110/G116/G32/G80/G32/G116/G111/G32/G103/G101/G116/G32/G100/G105/G102/G102/G101/G114/G101/G110/G116/G32/G112/G111/G115/G105/G116/G105/G111/G110/G115/G32/G111/G102/G32/G116/G104/G101/G32/G115/G116/G114/G97/G105/G103/G104/G116
/G119/G105/G114/G101/G32/G91/G115/G101/G101/G32/G70/G105/G103/G46/G32/G49/G48/G46/G51/G40/G105/G41/G93/G46
/G73/G110/G32/G118/G97/G114/G105/G111/G117/G115/G32/G112/G111/G115/G105/G116/G105/G111/G110/G115/G44/G32/G116/G104/G101/G32/G119/G105/G114/G101/G32/G105/G110/G116/G101/G114/G115/G101/G99/G116/G115/G32/G116/G104/G101
/G99/G105/G114/G99/G117/G108/G97/G114/G32/G119/G105/G114/G101/G32/G97/G116/G32/G80/G32/G97/G110/G100/G32/G97/G116/G32/G97/G110/G111/G116/G104/G101/G114/G32/G112/G111/G105/G110/G116/G32/G81/G49/G32/G111/G114/G32/G81/G50/G32/G111/G114
/G81/G51/G44/G32/G101/G116/G99/G46/G32/G73/G110/G32/G111/G110/G101/G32/G112/G111/G115/G105/G116/G105/G111/G110/G44/G32/G121/G111/G117/G32/G119/G105/G108/G108/G32/G115/G101/G101/G32/G116/G104/G97/G116/G32/G105/G116/G32/G119/G105/G108/G108
/G105/G110/G116/G101/G114/G115/G101/G99/G116/G32/G116/G104/G101/G32/G99/G105/G114/G99/G108/G101/G32/G97/G116/G32/G116/G104/G101/G32/G112/G111/G105/G110/G116/G32/G80/G32/G111/G110/G108/G121/G32/G40/G115/G101/G101/G32/G112/G111/G115/G105/G116/G105/G111/G110
/G65′/G66′/G32/G111/G102/G32/G65/G66/G41/G46/G32/G84/G104/G105/G115/G32/G115/G104/G111/G119/G115/G32/G116/G104/G97/G116/G32/G97/G32/G116/G97/G110/G103/G101/G110/G116/G32/G101/G120/G105/G115/G116/G115/G32/G97/G116
/G116/G104/G101/G32/G112/G111/G105/G110/G116/G32/G80/G32/G111/G102/G32/G116/G104/G101/G32/G99/G105/G114/G99/G108/G101/G46/G32/G79/G110/G32/G114/G111/G116/G97/G116/G105/G110/G103/G32/G102/G117/G114/G116/G104/G101/G114/G44/G32/G121/G111/G117
/G99/G97/G110/G32/G111/G98/G115/G101/G114/G118/G101/G32/G116/G104/G97/G116/G32/G105/G110/G32/G97/G108/G108/G32/G111/G116/G104/G101/G114/G32/G112/G111/G115/G105/G116/G105/G111/G110/G115/G32/G111/G102/G32/G65/G66/G44/G32/G105/G116/G32/G119/G105/G108/G108
/G105/G110/G116/G101/G114/G115/G101/G99/G116/G32/G116/G104/G101/G32/G99/G105/G114/G99/G108/G101/G32/G97/G116/G32/G80/G32/G97/G110/G100/G32/G97/G116/G32/G97/G110/G111/G116/G104/G101/G114/G32/G112/G111/G105/G110/G116/G44/G32/G115/G97/G121/G32/G82/G49
/G111/G114/G32/G82/G50/G32/G111/G114/G32/G82/G51/G44/G32/G101/G116/G99/G46/G32/G83/G111/G44/G32/G121/G111/G117/G32/G99/G97/G110/G32/G111/G98/G115/G101/G114/G118/G101/G32/G116/G104/G97/G116/G32/G116/G104/G101/G114/G101/G32/G105/G115
/G111/G110/G108/G121/G32/G111/G110/G101/G32/G116/G97/G110/G103/G101/G110/G116/G32/G97/G116/G32/G97/G32/G112/G111/G105/G110/G116/G32/G111/G102/G32/G116/G104/G101/G32/G99/G105/G114/G99/G108/G101/G46
/G87/G104/G105/G108/G101/G32/G100/G111/G105/G110/G103/G32/G97/G99/G116/G105/G118/G105/G116/G121/G32/G97/G98/G111/G118/G101/G44/G32/G121/G111/G117/G32/G109/G117/G115/G116/G32/G104/G97/G118/G101/G32/G111/G98/G115/G101/G114/G118/G101/G100/G32/G116/G104/G97/G116/G32/G97/G115/G32/G116/G104/G101/G32/G112/G111/G115/G105/G116/G105/G111/G110/G32/G65/G66
/G109/G111/G118/G101/G115/G32/G116/G111/G119/G97/G114/G100/G115/G32/G116/G104/G101/G32/G112/G111/G115/G105/G116/G105/G111/G110/G32/G65′/G32/G66′/G44/G32/G116/G104/G101/G32/G99/G111/G109/G109/G111/G110/G32/G112/G111/G105/G110/G116/G44/G32/G115/G97/G121/G32/G81/G49/G44/G32/G111/G102/G32/G116/G104/G101/G32/G108/G105/G110/G101/G32/G65/G66/G32/G97/G110/G100/G32/G116/G104/G101
/G99/G105/G114/G99/G108/G101/G32/G103/G114/G97/G100/G117/G97/G108/G108/G121/G32/G99/G111/G109/G101/G115/G32/G110/G101/G97/G114/G101/G114/G32/G97/G110/G100/G32/G110/G101/G97/G114/G101/G114/G32/G116/G111/G32/G116/G104/G101/G32/G99/G111/G109/G109/G111/G110/G32/G112/G111/G105/G110/G116/G32/G80/G46/G32/G85/G108/G116/G105/G109/G97/G116/G101/G108/G121/G44/G32/G105/G116/G32/G99/G111/G105/G110/G99/G105/G100/G101/G115
/G119/G105/G116/G104/G32/G116/G104/G101/G32/G112/G111/G105/G110/G116/G32/G80/G32/G105/G110/G32/G116/G104/G101/G32/G112/G111/G115/G105/G116/G105/G111/G110/G32/G65′/G66′/G32/G111/G102/G32/G65/G66/G46/G32/G65/G103/G97/G105/G110/G32/G110/G111/G116/G101/G44/G32/G119/G104/G97/G116/G32/G104/G97/G112/G112/G101/G110/G115/G32/G105/G102/G32/G65′′/G66′′/G32/G105/G115
/G114/G111/G116/G97/G116/G101/G100/G32/G114/G105/G103/G104/G116/G119/G97/G114/G100/G115/G32/G97/G98/G111/G117/G116/G32/G80/G63/G32/G84/G104/G101/G32/G99/G111/G109/G109/G111/G110/G32/G112/G111/G105/G110/G116/G32/G82/G51/G32/G103/G114/G97/G100/G117/G97/G108/G108/G121/G32/G99/G111/G109/G101/G115/G32/G110/G101/G97/G114/G101/G114/G32/G97/G110/G100/G32/G110/G101/G97/G114/G101/G114
/G116/G111/G32/G80/G32/G97/G110/G100/G32/G117/G108/G116/G105/G109/G97/G116/G101/G108/G121/G32/G99/G111/G105/G110/G99/G105/G100/G101/G115/G32/G119/G105/G116/G104/G32/G80/G46/G32/G83/G111/G44/G32/G119/G104/G97/G116/G32/G119/G101/G32/G115/G101/G101/G32/G105/G115/G58
/G84/G104/G101/G32/G116/G97/G110/G103/G101/G110/G116/G32/G116/G111/G32/G97/G32/G99/G105/G114/G99/G108/G101/G32/G105/G115/G32/G97/G32/G115/G112/G101/G99/G105/G97/G108/G32/G99/G97/G115/G101/G32/G111/G102/G32/G116/G104/G101/G32/G115/G101/G99/G97/G110/G116/G44/G32/G119/G104/G101/G110/G32/G116/G104/G101/G32/G116/G119/G111/G32/G101/G110/G100
/G112/G111/G105/G110/G116/G115/G32/G111/G102/G32/G105/G116/G115/G32/G99/G111/G114/G114/G101/G115/G112/G111/G110/G100/G105/G110/G103/G32/G99/G104/G111/G114/G100/G32/G99/G111/G105/G110/G99/G105/G100/G101/G46
/G70/G105/G103/G46/G32/G49/G48/G46/G51/G40/G105/G41
/G70/G105/G103/G46/G32/G49/G48/G46/G50
/G42/G84/G104/G101/G32/G119/G111/G114/G100/G32/G145/G116/G97/G110/G103/G101/G110/G116/G146/G32/G99/G111/G109/G101/G115/G32/G102/G114/G111/G109/G32/G116/G104/G101/G32/G76/G97/G116/G105/G110/G32/G119/G111/G114/G100/G32/G145/G116/G97/G110/G103/G101/G114/G101/G146/G44/G32/G119/G104/G105/G99/G104/G32/G109/G101/G97/G110/G115/G32/G116/G111/G32/G116/G111/G117/G99/G104/G32/G97/G110/G100/G32/G119/G97/G115
/G105/G110/G116/G114/G111/G100/G117/G99/G101/G100/G32/G98/G121/G32/G116/G104/G101/G32/G68/G97/G110/G105/G115/G104/G32/G109/G97/G116/G104/G101/G109/G97/G116/G105/G99/G105/G97/G110/G32/G84/G104/G111/G109/G97/G115/G32/G70/G105/G110/G101/G107/G101/G32/G105/G110/G32/G67/G46/G69/G46/G32/G49/G53/G56/G51/G46
```

### 3. pypdfium2 (Current)
```text

	 
	
			*			

	
			#$%+,				
"
	
		*
		
*
		
				
			*
'
		*
		 	
			
		*	
	"	-
				
"	*	*	
			
			
'
		
*"		
				

	

*
				

 	


'	 	
 
	 * 	 
		  		 
   	 
	    
	 
	 
	
!	
		
						
	
		
&
 !		
	()	
	
	"			
*
	"	
	*			()"				

	

	.
		#$%/0
'
 

			
	
	
		  
 	 '	
* 
		
	
				*
		

(′)′()!


		


			1	*
"
			

()
	
				
*2
22 	*"
		

	
	 		
	
 
3	*"	*
	"
		
	
()
	

	
(′)′	
* 		()	
	*	
					4	*	

		
(′)′()(		
(′′)′′

	
"-!	2*	
				
	*	
	
		
&
 		 

 		  
	

	 
 

		 
 
	
  
  
	


	


		
	

	
 		
	!
"
#$#%&#
```

---

## Sample 7 [CHUNK_ID: chk_976354316b72f080]
**Document:** STD-10/Std-10_Maths_EnglishMedium.pdf | **Page:** 105

### 1. PyMuPDF (fitz)
```text
-.


	
	
B
 AB
DE C AC
DF !2 2
3 "∠7!
7:7"C∠'!'$'5" 
	2	

!"3
∠:∠
∠$∠5
	∠:C∠$∠C∠5 ∠7C∠'∠:C∠$
∠C∠58777
Δ7:IΔ'$5

		2
	
$
	
	
	
	=
         	 
  	    	 	
	  	 

  	
 
  	 	 	 	
	


 	
 878 !8L7L8"

  	 

7	

(
7:  '$5  
AB
AC
DE
DF
=
!<,"∠7C∠'
!5.<0"';C7:'+
C7%;+
	
```

### 2. pypdf (Native)
```text
/G57/G48 /G77/G65 /G84/G72/G69/G77/G65 /G84/G73/G67/G83
/G70/G105/G103/G46/G32/G54/G46/G50/G55
/G72/G101/G114/G101/G44/G32/G121/G111/G117/G32/G109/G97/G121/G32/G111/G98/G115/G101/G114/G118/G101/G32/G116/G104/G97/G116/G32AB
DE/G32/G61/G32AC
DF /G32/G40/G101/G97/G99/G104/G32/G101/G113/G117/G97/G108/G32/G116/G111/G322
3/G41/G32/G97/G110/G100/G32∠/G32/G65/G32/G40/G105/G110/G99/G108/G117/G100/G101/G100
/G98/G101/G116/G119/G101/G101/G110/G32/G116/G104/G101/G32/G115/G105/G100/G101/G115/G32/G65/G66/G32/G97/G110/G100/G32/G65/G67/G41/G32/G61/G32∠/G32/G68/G32/G40/G105/G110/G99/G108/G117/G100/G101/G100/G32/G98/G101/G116/G119/G101/G101/G110/G32/G116/G104/G101/G32/G115/G105/G100/G101/G115/G32/G68/G69/G32/G97/G110/G100/G32/G68/G70/G41/G46/G32/G84/G104/G97/G116
/G105/G115/G44/G32/G111/G110/G101/G32/G97/G110/G103/G108/G101/G32/G111/G102/G32/G97/G32/G116/G114/G105/G97/G110/G103/G108/G101/G32/G105/G115/G32/G101/G113/G117/G97/G108/G32/G116/G111/G32/G111/G110/G101/G32/G97/G110/G103/G108/G101/G32/G111/G102/G32/G97/G110/G111/G116/G104/G101/G114/G32/G116/G114/G105/G97/G110/G103/G108/G101/G32/G97/G110/G100/G32/G115/G105/G100/G101/G115/G32/G105/G110/G99/G108/G117/G100/G105/G110/G103
/G116/G104/G101/G115/G101/G32/G97/G110/G103/G108/G101/G115/G32/G97/G114/G101/G32/G105/G110/G32/G116/G104/G101/G32/G115/G97/G109/G101/G32/G114/G97/G116/G105/G111/G32/G40/G105/G46/G101/G46/G44/G32/G112/G114/G111/G112/G111/G114/G116/G105/G111/G110/G41/G46/G32/G78/G111/G119/G32/G108/G101/G116/G32/G117/G115/G32/G109/G101/G97/G115/G117/G114/G101/G32∠/G32/G66/G44/G32∠/G32/G67/G44
∠/G32/G69/G32/G97/G110/G100/G32∠/G32/G70/G46
/G89/G111/G117/G32/G119/G105/G108/G108/G32/G102/G105/G110/G100/G32/G116/G104/G97/G116/G32∠/G32/G66/G32/G61/G32∠/G32/G69/G32/G97/G110/G100/G32∠/G32/G67/G32/G61/G32∠/G32/G70/G46/G32/G84/G104/G97/G116/G32/G105/G115/G44/G32∠/G32/G65/G32/G61/G32∠/G32/G68/G44/G32∠/G32/G66/G32/G61/G32∠/G32/G69/G32/G97/G110/G100
∠/G32/G67/G32/G61/G32∠/G32/G70/G46/G32/G83/G111/G44/G32/G98/G121/G32/G65/G65/G65/G32/G115/G105/G109/G105/G108/G97/G114/G105/G116/G121/G32/G99/G114/G105/G116/G101/G114/G105/G111/G110/G44/G32Δ/G32/G65/G66/G67/G32/G126/G32Δ/G32/G68/G69/G70/G46/G32/G89/G111/G117/G32/G109/G97/G121/G32/G114/G101/G112/G101/G97/G116/G32/G116/G104/G105/G115
/G97/G99/G116/G105/G118/G105/G116/G121/G32/G98/G121/G32/G100/G114/G97/G119/G105/G110/G103/G32/G115/G101/G118/G101/G114/G97/G108/G32/G112/G97/G105/G114/G115/G32/G111/G102/G32/G115/G117/G99/G104/G32/G116/G114/G105/G97/G110/G103/G108/G101/G115/G32/G119/G105/G116/G104/G32/G111/G110/G101/G32/G97/G110/G103/G108/G101/G32/G111/G102/G32/G97/G32/G116/G114/G105/G97/G110/G103/G108/G101/G32/G101/G113/G117/G97/G108/G32/G116/G111
/G111/G110/G101/G32/G97/G110/G103/G108/G101/G32/G111/G102/G32/G97/G110/G111/G116/G104/G101/G114/G32/G116/G114/G105/G97/G110/G103/G108/G101/G32/G97/G110/G100/G32/G116/G104/G101/G32/G115/G105/G100/G101/G115/G32/G105/G110/G99/G108/G117/G100/G105/G110/G103/G32/G116/G104/G101/G115/G101/G32/G97/G110/G103/G108/G101/G115/G32/G97/G114/G101/G32/G112/G114/G111/G112/G111/G114/G116/G105/G111/G110/G97/G108/G46
/G69/G118/G101/G114/G121/G116/G105/G109/G101/G44/G32/G121/G111/G117/G32/G119/G105/G108/G108/G32/G102/G105/G110/G100/G32/G116/G104/G97/G116/G32/G116/G104/G101/G32/G116/G114/G105/G97/G110/G103/G108/G101/G115/G32/G97/G114/G101/G32/G115/G105/G109/G105/G108/G97/G114/G46/G32/G73/G116/G32/G105/G115/G32/G100/G117/G101/G32/G116/G111/G32/G116/G104/G101/G32/G102/G111/G108/G108/G111/G119/G105/G110/G103/G32/G99/G114/G105/G116/G101/G114/G105/G111/G110
/G111/G102/G32/G115/G105/G109/G105/G108/G97/G114/G105/G116/G121/G32/G111/G102/G32/G116/G114/G105/G97/G110/G103/G108/G101/G115/G58
/G84/G104/G101/G111/G114/G101/G109/G32/G54/G46/G53/G32/G58/G32/G73/G102/G32/G111/G110/G101/G32/G97/G110/G103/G108/G101/G32/G111/G102/G32/G97/G32/G116/G114/G105/G97/G110/G103/G108/G101/G32/G105/G115/G32/G101/G113/G117/G97/G108/G32/G116/G111/G32/G111/G110/G101/G32/G97/G110/G103/G108/G101/G32/G111/G102/G32/G116/G104/G101/G32/G111/G116/G104/G101/G114
/G116/G114/G105/G97/G110/G103/G108/G101/G32
/G97/G110/G100/G32/G116/G104/G101/G32/G115/G105/G100/G101/G115/G32/G105/G110/G99/G108/G117/G100/G105/G110/G103/G32/G116/G104/G101/G115/G101/G32/G97/G110/G103/G108/G101/G115/G32/G97/G114/G101/G32/G112/G114/G111/G112/G111/G114/G116/G105/G111/G110/G97/G108/G44/G32/G116/G104/G101/G110/G32/G116/G104/G101/G32/G116/G119/G111
/G116/G114/G105/G97/G110/G103/G108/G101/G115/G32/G97/G114/G101/G32/G115/G105/G109/G105/G108/G97/G114/G46
/G84/G104/G105/G115/G32/G99/G114/G105/G116/G101/G114/G105/G111/G110/G32/G105/G115/G32/G114/G101/G102/G101/G114/G114/G101/G100/G32/G116/G111/G32/G97/G115
/G116/G104/G101/G32 /G83/G65/G83/G32/G40/G83/G105/G100/G101/G150/G65/G110/G103/G108/G101/G150/G83/G105/G100/G101/G41
/G115/G105/G109/G105/G108/G97/G114/G105/G116/G121/G32/G99/G114/G105/G116/G101/G114/G105/G111/G110/G32/G102/G111/G114/G32/G116/G119/G111
/G116/G114/G105/G97/G110/G103/G108/G101/G115/G46
/G65/G115/G32/G98/G101/G102/G111/G114/G101/G44/G32/G116/G104/G105/G115/G32/G116/G104/G101/G111/G114/G101/G109/G32/G99/G97/G110
/G98/G101/G32/G112/G114/G111/G118/G101/G100/G32/G98/G121/G32/G116/G97/G107/G105/G110/G103/G32/G116/G119/G111/G32/G116/G114/G105/G97/G110/G103/G108/G101/G115
/G65/G66/G67/G32 /G97/G110/G100/G32 /G68/G69/G70/G32 /G115/G117/G99/G104/G32 /G116/G104/G97/G116
AB AC
DE DF= /G32/G40</G32/G49/G41/G32/G97/G110/G100/G32∠/G32/G65/G32/G61/G32∠/G32/G68
/G40/G115/G101/G101/G32/G70/G105/G103/G46/G32/G54/G46/G50/G56/G41/G46/G32/G67/G117/G116/G32/G68/G80/G32/G61/G32/G65/G66/G44/G32/G68/G81
/G61/G32/G65/G67/G32/G97/G110/G100/G32/G106/G111/G105/G110/G32/G80/G81/G46
/G70/G105/G103/G46/G32/G54/G46/G50/G56
```

### 3. pypdfium2 (Current)
```text
-. 

	
 	
B

AB
DE C
AC
DF !2
2
3 "∠7!
7:7"C∠'!'$'5" 
	2	

!"3
∠:∠
∠$∠5
	∠:C∠$∠C∠5 ∠7C∠'∠:C∠$
∠C∠58777
Δ7:IΔ'$5

		2
	
$
	
	
	
	=
        	
 	   	 	
	  	 

  	
 
  	 	 	 	
	
  

 	
 878 !8L7L8"

  	 

7 	
 
(
7:  '$5  
AB AC
DE DF = !<,"∠7C∠'
!5.<0"';C7:'+
C7%;+
 	
```

---

## Sample 8 [CHUNK_ID: chk_a45963ae777c2e84]
**Document:** STD-10/Std-10_Science_English Medium.pdf | **Page:** 209

### 1. PyMuPDF (fitz)
```text
Science
196
12.1 MAGNETIC FIELD AND FIELD LINES
12.1 MAGNETIC FIELD AND FIELD LINES
12.1 MAGNETIC FIELD AND FIELD LINES
12.1 MAGNETIC FIELD AND FIELD LINES
12.1 MAGNETIC FIELD AND FIELD LINES
We are familiar with the fact that a compass needle gets deflected when
brought near a bar magnet. A compass needle is, in fact, a small bar
magnet. The ends of the compass needle point approximately towards
north and south directions. The end pointing towards north is called north
seeking or north pole. The other end that points towards south is called
south seeking or south pole. Through various activities we have observed
that like poles repel, while unlike poles of magnets attract each other.
Q
U
E
S
T
I
O
N
?
1.
Why does a compass needle get deflected when brought near
a bar magnet?
Activity 12.2
Activity 12.2
Activity 12.2
Activity 12.2
Activity 12.2
n
Fix a sheet of white paper on a drawing
board using some adhesive material.
n
Place a bar magnet in the centre of it.
n
Sprinkle some iron filings uniformly
around the bar magnet (Fig. 12.2). A
salt-sprinkler may be used for this
purpose.
n
Now tap the board gently.
n
What do you observe?
Figure 12.2
Figure 12.2
Figure 12.2
Figure 12.2
Figure 12.2
Iron filings near the bar magnet align
themselves along the field lines.
The iron filings arrange themselves in a pattern as shown
Fig. 12.2.  Why do the iron filings arrange in such a pattern? What does
this pattern demonstrate?  The magnet exerts its influence in the region
surrounding it.  Therefore the iron filings experience a force.  The force
thus exerted makes iron filings to arrange in a pattern. The region
surrounding a magnet, in which the force of the magnet can be detected,
is said to have a magnetic field.  The lines along which the iron filings
align themselves represent magnetic field lines.
Are there other ways of obtaining magnetic field lines around a bar
magnet?  Yes, you can yourself draw the field lines of a bar magnet.
Activity 12.3
Activity 12.3
Activity 12.3
Activity 12.3
Activity 12.3
n
Take a small compass and a bar magnet.
n
Place the magnet on a sheet of white paper fixed on a drawing
board, using some adhesive material.
n
Mark the boundary of the magnet.
n
Place the compass near the north pole of the magnet. How does
it behave? The south pole of the needle points towards the north
pole of the magnet. The north pole of the compass is directed
away from the north pole of the magnet.
```

### 2. pypdf (Native)
```text
Science196
12.1 MAGNETIC FIELD AND FIELD LINES12.1 MAGNETIC FIELD AND FIELD LINES12.1 MAGNETIC FIELD AND FIELD LINES12.1 MAGNETIC FIELD AND FIELD LINES12.1 MAGNETIC FIELD AND FIELD LINES
We are familiar with the fact that a compass needle gets deflected when
brought near a bar magnet. A compass needle is, in fact, a small bar
magnet. The ends of the compass needle point approximately towards
north and south directions. The end pointing towards north is called north
seeking or north pole. The other end that points towards south is called
south seeking or south pole. Through various activities we have observed
that like poles repel, while unlike poles of magnets attract each other.
QUESTION
?
1. Why does a compass needle get deflected when brought near
a bar magnet?
Activity 12.2Activity 12.2Activity 12.2Activity 12.2Activity 12.2
/square6Fix a sheet of white paper on a drawing
board using some adhesive material.
/square6Place a bar magnet in the centre of it.
/square6Sprinkle some iron filings uniformly
around the bar magnet (Fig. 12.2). A
salt-sprinkler may be used for this
purpose.
/square6Now tap the board gently.
/square6What do you observe?
 Figure 12.2Figure 12.2Figure 12.2Figure 12.2Figure 12.2
Iron filings near the bar magnet align
themselves along the field lines.
The iron filings arrange themselves in a pattern as shown
Fig. 12.2.  Why do the iron filings arrange in such a pattern? What does
this pattern demonstrate?  The magnet exerts its influence in the region
surrounding it.  Therefore the iron filings experience a force.  The force
thus exerted makes iron filings to arrange in a pattern. The region
surrounding a magnet, in which the force of the magnet can be detected,
is said to have a magnetic field.  The lines along which the iron filings
align themselves represent magnetic field lines.
Are there other ways of obtaining magnetic field lines around a bar
magnet?  Yes, you can yourself draw the field lines of a bar magnet.
Activity 12.3Activity 12.3Activity 12.3Activity 12.3Activity 12.3
/square6Take a small compass and a bar magnet.
/square6Place the magnet on a sheet of white paper fixed on a drawing
board, using some adhesive material.
/square6Mark the boundary of the magnet.
/square6Place the compass near the north pole of the magnet. How does
it behave? The south pole of the needle points towards the north
pole of the magnet. The north pole of the compass is directed
away from the north pole of the magnet.
```

### 3. pypdfium2 (Current)
```text
196 Science
12.1 MAGNETIC FIELD AND FIELD LINES
We are familiar with the fact that a compass needle gets deflected when
brought near a bar magnet. A compass needle is, in fact, a small bar
magnet. The ends of the compass needle point approximately towards
north and south directions. The end pointing towards north is called north
seeking or north pole. The other end that points towards south is called
south seeking or south pole. Through various activities we have observed
that like poles repel, while unlike poles of magnets attract each other.
QUESTION
?
1. Why does a compass needle get deflected when brought near
a bar magnet?
Activity 12.2
n Fix a sheet of white paper on a drawing
board using some adhesive material.
n Place a bar magnet in the centre of it.
n Sprinkle some iron filings uniformly
around the bar magnet (Fig. 12.2). A
salt-sprinkler may be used for this
purpose.
n Now tap the board gently.
n What do you observe? Figure 12.2
Iron filings near the bar magnet align
themselves along the field lines.
The iron filings arrange themselves in a pattern as shown
Fig. 12.2. Why do the iron filings arrange in such a pattern? What does
this pattern demonstrate? The magnet exerts its influence in the region
surrounding it. Therefore the iron filings experience a force. The force
thus exerted makes iron filings to arrange in a pattern. The region
surrounding a magnet, in which the force of the magnet can be detected,
is said to have a magnetic field. The lines along which the iron filings
align themselves represent magnetic field lines.
Are there other ways of obtaining magnetic field lines around a bar
magnet? Yes, you can yourself draw the field lines of a bar magnet.
Activity 12.3
n Take a small compass and a bar magnet.
n Place the magnet on a sheet of white paper fixed on a drawing
board, using some adhesive material.
n Mark the boundary of the magnet.
n Place the compass near the north pole of the magnet. How does
it behave? The south pole of the needle points towards the north
pole of the magnet. The north pole of the compass is directed
away from the north pole of the magnet.
```

---

## Sample 9 [CHUNK_ID: chk_bae6b26601ea2383]
**Document:** STD-10/Std-10_Maths_EnglishMedium.pdf | **Page:** 91

### 1. PyMuPDF (fitz)
```text

	
	
						

	
	

	
			
					
		
	
	


	
 
!
		
"	
	#$%&'
     	

(
	$%&'		
)*    	 	 	
$′%′&′'′	+,-
#$′%′&′'′	



#$%&'(			
	
	
	
$′	!$%′	!%&′
	!&'′	!'(	#	$′%′&′'′$%&'
	
		.	
/#$′%′&′'′		
#$%&'0		
#$%&'		
#$′%′&′'′
1	2$′		2$2%′
		2%2&′		2&2'′		
2'/
					$′ ↔$%′ ↔%
&′ ↔&'′ ↔'%
				
#	

∠$3∠$′∠%3∠%′∠&3∠&′∠'3∠'′
 AB
BC
CD
DA
A B
B C
C D
D A
=
=
=
′ ′
′ ′
′
′
′
′

(	
				


	
						


```

### 2. pypdf (Native)
```text
/G55/G54 /G77/G65 /G84/G72/G69/G77/G65 /G84/G73/G67/G83
/G78/G111/G116/G101/G32/G116/G104/G97/G116/G32/G116/G104/G101/G32/G115/G97/G109/G101/G32/G114/G97/G116/G105/G111/G32/G111/G102/G32/G116/G104/G101/G32/G99/G111/G114/G114/G101/G115/G112/G111/G110/G100/G105/G110/G103/G32/G115/G105/G100/G101/G115/G32/G105/G115/G32/G114/G101/G102/G101/G114/G114/G101/G100/G32/G116/G111/G32/G97/G115/G32/G116/G104/G101/G32/G115/G99/G97/G108/G101
/G102/G97/G99/G116/G111/G114/G32/G40/G111/G114/G32/G116/G104/G101/G32/G82/G101/G112/G114/G101/G115/G101/G110/G116/G97/G116/G105/G118/G101/G32/G70/G114/G97/G99/G116/G105/G111/G110/G41/G32/G102/G111/G114/G32/G116/G104/G101/G32/G112/G111/G108/G121/G103/G111/G110/G115/G46/G32/G89/G111/G117/G32/G109/G117/G115/G116/G32/G104/G97/G118/G101/G32/G104/G101/G97/G114/G100/G32/G116/G104/G97/G116
/G119/G111/G114/G108/G100/G32/G109/G97/G112/G115/G32/G40/G105/G46/G101/G46/G44/G32/G103/G108/G111/G98/G97/G108/G32/G109/G97/G112/G115/G41/G32/G97/G110/G100/G32/G98/G108/G117/G101/G32/G112/G114/G105/G110/G116/G115/G32/G102/G111/G114/G32/G116/G104/G101/G32/G99/G111/G110/G115/G116/G114/G117/G99/G116/G105/G111/G110/G32/G111/G102/G32/G97/G32/G98/G117/G105/G108/G100/G105/G110/G103/G32/G97/G114/G101
/G112/G114/G101/G112/G97/G114/G101/G100/G32/G117/G115/G105/G110/G103/G32/G97/G32/G115/G117/G105/G116/G97/G98/G108/G101/G32/G115/G99/G97/G108/G101/G32/G102/G97/G99/G116/G111/G114/G32/G97/G110/G100/G32/G111/G98/G115/G101/G114/G118/G105/G110/G103/G32/G99/G101/G114/G116/G97/G105/G110/G32/G99/G111/G110/G118/G101/G110/G116/G105/G111/G110/G115/G46
/G73/G110/G32/G111/G114/G100/G101/G114/G32/G116/G111/G32/G117/G110/G100/G101/G114/G115/G116/G97/G110/G100/G32/G115/G105/G109/G105/G108/G97/G114/G105/G116/G121/G32/G111/G102/G32/G102/G105/G103/G117/G114/G101/G115/G32/G109/G111/G114/G101/G32/G99/G108/G101/G97/G114/G108/G121/G44/G32/G108/G101/G116/G32/G117/G115/G32/G112/G101/G114/G102/G111/G114/G109/G32/G116/G104/G101/G32/G102/G111/G108/G108/G111/G119/G105/G110/G103
/G97/G99/G116/G105/G118/G105/G116/G121/G58
/G65/G99/G116/G105/G118/G105/G116/G121/G32 /G49/G32 /G58/G32/G32/G80/G108/G97/G99/G101/G32/G97/G32/G108/G105/G103/G104/G116/G101/G100/G32/G98/G117/G108/G98/G32/G97/G116/G32/G97
/G112/G111/G105/G110/G116/G32/G79/G32
/G111/G110/G32/G116/G104/G101/G32/G99/G101/G105/G108/G105/G110/G103/G32/G32/G97/G110/G100/G32/G100/G105/G114/G101/G99/G116/G108/G121/G32/G98/G101/G108/G111/G119
/G105/G116/G32/G97/G32/G116/G97/G98/G108/G101/G32/G105/G110/G32/G121/G111/G117/G114/G32/G99/G108/G97/G115/G115/G114/G111/G111/G109/G46/G32/G76/G101/G116/G32/G117/G115/G32/G99/G117/G116/G32/G97
/G112/G111/G108/G121/G103/G111/G110/G44/G32/G115/G97/G121/G32/G97/G32/G113/G117/G97/G100/G114/G105/G108/G97/G116/G101/G114/G97/G108/G32/G65/G66/G67/G68/G44/G32/G102/G114/G111/G109
/G97/G32/G112/G108/G97/G110/G101/G32/G99/G97/G114/G100/G98/G111/G97/G114/G100/G32/G97/G110/G100/G32/G112/G108/G97/G99/G101/G32/G116/G104/G105/G115
/G99/G97/G114/G100/G98/G111/G97/G114/G100/G32/G112/G97/G114/G97/G108/G108/G101/G108/G32/G116/G111/G32/G116/G104/G101/G32/G103/G114/G111/G117/G110/G100/G32/G98/G101/G116/G119/G101/G101/G110
/G116/G104/G101/G32/G108/G105/G103/G104/G116/G101/G100/G32/G98/G117/G108/G98/G32/G32/G97/G110/G100/G32/G116/G104/G101/G32/G116/G97/G98/G108/G101/G46/G32/G84/G104/G101/G110/G32/G97
/G115/G104/G97/G100/G111/G119/G32/G111/G102/G32/G65/G66/G67/G68/G32/G105/G115/G32/G99/G97/G115/G116/G32/G111/G110/G32/G116/G104/G101/G32/G116/G97/G98/G108/G101/G46
/G77/G97/G114/G107/G32/G116/G104/G101/G32/G111/G117/G116/G108/G105/G110/G101/G32/G111/G102/G32/G116/G104/G105/G115/G32/G115/G104/G97/G100/G111/G119/G32/G97/G115
/G65′/G66′/G67′/G68′/G32/G40/G115/G101/G101/G32/G70/G105/G103/G46/G54/G46/G52/G41/G46
/G78/G111/G116/G101/G32/G116/G104/G97/G116/G32/G116/G104/G101/G32/G113/G117/G97/G100/G114/G105/G108/G97/G116/G101/G114/G97/G108/G32/G65′/G66′/G67′/G68′/G32/G32/G105/G115
/G97/G110/G32/G101/G110/G108/G97/G114/G103/G101/G109/G101/G110/G116/G32/G40/G111/G114/G32/G109/G97/G103/G110/G105/G102/G105/G99/G97/G116/G105/G111/G110/G41/G32/G111/G102/G32/G32/G116/G104/G101
/G113/G117/G97/G100/G114/G105/G108/G97/G116/G101/G114/G97/G108/G32/G65/G66/G67/G68/G46/G32/G84/G104/G105/G115/G32/G105/G115/G32/G98/G101/G99/G97/G117/G115/G101/G32/G111/G102
/G116/G104/G101/G32/G112/G114/G111/G112/G101/G114/G116/G121/G32/G111/G102/G32/G108/G105/G103/G104/G116/G32/G116/G104/G97/G116/G32/G108/G105/G103/G104/G116/G32/G112/G114/G111/G112/G111/G103/G97/G116/G101/G115
/G105/G110/G32/G97/G32/G115/G116/G114/G97/G105/G103/G104/G116/G32/G108/G105/G110/G101/G46/G32/G89/G111/G117/G32/G109/G97/G121/G32/G97/G108/G115/G111/G32/G110/G111/G116/G101/G32/G116/G104/G97/G116
/G65′/G32/G108/G105/G101/G115/G32/G111/G110/G32/G114/G97/G121/G32/G79/G65/G44/G32/G66′/G32/G108/G105/G101/G115/G32/G111/G110/G32/G114/G97/G121/G32/G79/G66/G44/G32/G67′
/G108/G105/G101/G115/G32/G111/G110/G32/G32/G79/G67/G32/G97/G110/G100/G32/G68′/G32/G108/G105/G101/G115/G32/G111/G110/G32/G79/G68/G46/G32/G32/G84/G104/G117/G115/G44/G32/G113/G117/G97/G100/G114/G105/G108/G97/G116/G101/G114/G97/G108/G115/G32/G65′/G66′/G67′/G68′/G32/G32/G97/G110/G100/G32/G65/G66/G67/G68/G32/G97/G114/G101/G32/G111/G102/G32/G116/G104/G101
/G115/G97/G109/G101/G32/G115/G104/G97/G112/G101/G32/G98/G117/G116/G32/G111/G102/G32/G100/G105/G102/G102/G101/G114/G101/G110/G116/G32/G115/G105/G122/G101/G115/G46
/G83/G111/G44/G32/G113/G117/G97/G100/G114/G105/G108/G97/G116/G101/G114/G97/G108/G32/G32/G65′/G66′/G67′/G68′/G32/G32/G105/G115/G32/G115/G105/G109/G105/G108/G105/G97/G114/G32/G116/G111/G32/G113/G117/G97/G100/G114/G105/G108/G97/G116/G101/G114/G97/G108/G32/G65/G66/G67/G68/G46/G32/G87/G101/G32/G99/G97/G110/G32/G97/G108/G115/G111/G32/G115/G97/G121
/G116/G104/G97/G116/G32/G113/G117/G97/G100/G114/G105/G108/G97/G116/G101/G114/G97/G108/G32/G65/G66/G67/G68/G32/G105/G115/G32/G115/G105/G109/G105/G108/G97/G114/G32/G116/G111/G32/G116/G104/G101/G32/G113/G117/G97/G100/G114/G105/G108/G97/G116/G101/G114/G97/G108/G32/G65′/G66′/G67′/G68′/G46
/G72/G101/G114/G101/G44/G32/G121/G111/G117/G32/G99/G97/G110/G32/G97/G108/G115/G111/G32/G110/G111/G116/G101/G32/G116/G104/G97/G116/G32/G118/G101/G114/G116/G101/G120/G32/G65′/G32/G99/G111/G114/G114/G101/G115/G112/G111/G110/G100/G115/G32/G116/G111/G32/G118/G101/G114/G116/G101/G120/G32/G65/G44/G32/G118/G101/G114/G116/G101/G120/G32/G66′
/G99/G111/G114/G114/G101/G115/G112/G111/G110/G100/G115/G32/G116/G111/G32/G118/G101/G114/G116/G101/G120/G32/G66/G44/G32/G118/G101/G114/G116/G101/G120/G32/G67′/G32/G99/G111/G114/G114/G101/G115/G112/G111/G110/G100/G115/G32/G116/G111/G32/G118/G101/G114/G116/G101/G120/G32/G67/G32/G97/G110/G100/G32/G118/G101/G114/G116/G101/G120/G32/G32/G68′/G32/G99/G111/G114/G114/G101/G115/G112/G111/G110/G100/G115
/G116/G111/G32/G118/G101/G114/G116/G101/G120/G32/G68/G46/G32/G83/G121/G109/G98/G111/G108/G105/G99/G97/G108/G108/G121/G44/G32/G116/G104/G101/G115/G101/G32/G99/G111/G114/G114/G101/G115/G112/G111/G110/G100/G101/G110/G99/G101/G115/G32/G97/G114/G101/G32/G114/G101/G112/G114/G101/G115/G101/G110/G116/G101/G100/G32/G97/G115/G32/G65′ ↔/G32/G65/G44/G32/G66′ ↔/G32/G66/G44
/G67′ ↔/G32/G67/G32/G97/G110/G100/G32/G68′ ↔/G32/G68/G46/G32/G66/G121/G32/G97/G99/G116/G117/G97/G108/G108/G121/G32/G109/G101/G97/G115/G117/G114/G105/G110/G103/G32/G116/G104/G101/G32/G97/G110/G103/G108/G101/G115/G32/G97/G110/G100/G32/G116/G104/G101/G32/G115/G105/G100/G101/G115/G32/G111/G102/G32/G116/G104/G101/G32/G116/G119/G111
/G113/G117/G97/G100/G114/G105/G108/G97/G116/G101/G114/G97/G108/G115/G44/G32/G121/G111/G117/G32/G109/G97/G121/G32/G118/G101/G114/G105/G102/G121/G32/G116/G104/G97/G116
/G40/G105/G41/G32∠/G32/G65/G32/G61/G32∠/G32/G65′/G44/G32∠/G32/G66/G32/G61/G32∠/G32/G66′/G44/G32∠/G32/G67/G32/G61/G32∠/G32/G67′/G44/G32∠/G32/G68/G32/G61/G32∠/G32/G68′/G32/G97/G110/G100
/G40/G105/G105/G41/G32
/G32AB BC CD DA
AB BC CD DA===′′ ′′ ′′ ′′
/G46
/G84/G104/G105/G115/G32/G97/G103/G97/G105/G110/G32/G101/G109/G112/G104/G97/G115/G105/G115/G101/G115/G32/G116/G104/G97/G116/G32/G116/G119/G111/G32 /G112/G111/G108/G121/G103/G111/G110/G115/G32 /G111/G102/G32 /G116/G104/G101/G32 /G115/G97/G109/G101/G32 /G110/G117/G109/G98/G101/G114/G32 /G111/G102/G32 /G115/G105/G100/G101/G115/G32 /G97/G114/G101
/G115/G105/G109/G105/G108/G97/G114 /G44/G32/G105/G102/G32/G40/G105/G41/G32/G97/G108/G108/G32/G116/G104/G101/G32/G99/G111/G114/G114/G101/G115/G112/G111/G110/G100/G105/G110/G103/G32/G97/G110/G103/G108/G101/G115/G32/G97/G114/G101/G32/G101/G113/G117/G97/G108/G32/G97/G110/G100/G32/G40/G105/G105/G41/G32/G97/G108/G108/G32/G116/G104/G101/G32/G99/G111/G114/G114/G101/G115/G112/G111/G110/G100/G105/G110/G103
/G115/G105/G100/G101/G115/G32 /G97/G114/G101/G32 /G105/G110/G32 /G116/G104/G101/G32 /G115/G97/G109/G101/G32 /G114/G97/G116/G105/G111/G32/G40/G111/G114/G32 /G112/G114/G111/G112/G111/G114/G116/G105/G111/G110/G41/G46
/G70/G105/G103/G46/G32 /G54/G46/G52
```

### 3. pypdfium2 (Current)
```text
 	
	
						

	
	

	
			
					
		
	
	


 	 
     
!
		
"	
	#$%&'

     	

 (
	 $%&'	 	 
)*  	 	 	
$′%′&′'′ 	 +,-
#$′%′&′'′	



#$%&'(			
	
	
	
$′	!$%′	!%&′
	!&'′	!'(	#	$′%′&′'′$%&'
	
		.	
/#$′%′&′'′		
#$%&'0		
#$%&'		
#$′%′&′'′
1   	  2$′ 		 2$ 2%′
		2%2&′		2&2'′		
2'/
					$′ ↔$%′ ↔%
&′ ↔&'′ ↔'%
		 		 
#	

∠$3∠$′∠%3∠%′∠&3∠&′∠'3∠'′ 
 AB BC CD DA
AB BC CD DA === ′′ ′′ ′′ ′′ 
(	  
			 	 
   
  
	
						
    
 
```

---

## Sample 10 [CHUNK_ID: chk_95b42f6c761a5d1d]
**Document:** STD-10/Std-10_Science_English Medium.pdf | **Page:** 128

### 1. PyMuPDF (fitz)
```text
How do Organisms Reproduce?
115
Figure 7.1(a)
Figure 7.1(a)
Figure 7.1(a)
Figure 7.1(a)
Figure 7.1(a) Binary fission in Amoeba
Activity 7.2
Activity 7.2
Activity 7.2
Activity 7.2
Activity 7.2
7.2 MODES OF REPRODUCTION USED BY SINGLE
7.2 MODES OF REPRODUCTION USED BY SINGLE
7.2 MODES OF REPRODUCTION USED BY SINGLE
7.2 MODES OF REPRODUCTION USED BY SINGLE
7.2 MODES OF REPRODUCTION USED BY SINGLE
ORGANISMS
ORGANISMS
ORGANISMS
ORGANISMS
ORGANISMS
Activity 7.1
Activity 7.1
Activity 7.1
Activity 7.1
Activity 7.1
n
Dissolve about 10 gm of sugar in 100 mL of water.
n
Take 20 mL of this solution in a test tube and add a pinch of yeast
granules to it.
n
Put a cotton plug on the mouth of the test tube and keep it in a
warm place.
n
After 1 or 2 hours, put a small drop of yeast culture from the test
tube on a slide and cover it with a coverslip.
n
Observe the slide under a microscope.
n
Wet a slice of bread, and keep it in a cool, moist and dark place.
n
Observe the surface of the slice with a magnifying glass.
n
Record your observations for a week.
Compare and contrast the ways in which yeast grows in the first
case, and how mould grows in the second.
Having discussed the context in which reproductive processes work,
let us now examine how different organisms actually reproduce. The
modes by which various organisms reproduce depend on the body
design of the organisms.
7.2.1 Fission
For unicellular organisms, cell division, or fission, leads to the creation
of new individuals. Many different patterns of fission have been observed.
Many bacteria and protozoa simply split into two equal halves during
cell division. In organisms such as Amoeba, the splitting of the two cells
during division can take place in any plane.
Activity 7.3
Activity 7.3
Activity 7.3
Activity 7.3
Activity 7.3
n
Observe a permanent slide of
Amoeba under a microscope.
n
Similarly 
observe 
another
permanent slide of Amoeba
showing binary fission.
n
Now, compare the observations of
both the slides.
However, some unicellular organisms
show somewhat more organisation of their
bodies, such as is seen in Leishmania (which
cause kala-azar), which have a whip-like
structure at one end of the cell. In such
organisms, binary fission occurs in a definite orientation in relation to
Figure 7.1(b)
Figure 7.1(b)
Figure 7.1(b)
Figure 7.1(b)
Figure 7.1(b) Binary fission in Leishmania
  (a)         (b)          (c)          (d)            (e)                        (f)
```

### 2. pypdf (Native)
```text
How do Organisms Reproduce? 115
Figure 7.1(a)Figure 7.1(a)Figure 7.1(a)Figure 7.1(a)Figure 7.1(a)  Binary fission in Amoeba
Activity 7.2Activity 7.2Activity 7.2Activity 7.2Activity 7.2
7.2 MODES OF REPRODUCTION USED BY SINGLE7.2 MODES OF REPRODUCTION USED BY SINGLE7.2 MODES OF REPRODUCTION USED BY SINGLE7.2 MODES OF REPRODUCTION USED BY SINGLE7.2 MODES OF REPRODUCTION USED BY SINGLE
ORGANISMSORGANISMSORGANISMSORGANISMSORGANISMS
Activity 7.1Activity 7.1Activity 7.1Activity 7.1Activity 7.1
/square6Dissolve about 10 gm of sugar in 100 mL of water .
/square6Take 20 mL of this solution in a test tube and add a pinch of yeast
granules to it.
/square6Put a cotton plug on the mouth of the test tube and keep it in a
warm place.
/square6After 1 or 2 hours, put a small drop of yeast culture from the test
tube on a slide and cover it with a coverslip.
/square6Observe the slide under a microscope.
/square6Wet a slice of br ead, and keep it in a cool, moist and dark place.
/square6Observe the surface of the slice with a magnifying glass.
/square6Record your observations for a week.
Compare and contrast the ways in which yeast grows in the first
case, and how mould grows in the second.
Having discussed the context in which reproductive processes work,
let us now examine how different organisms actually reproduce. The
modes by which various organisms reproduce depend on the body
design of the organisms.
7.2.1 Fission
For unicellular organisms, cell division, or fission, leads to the creation
of new individuals. Many different patterns of fission have been observed.
Many bacteria and protozoa simply split into two equal halves during
cell division. In organisms such as Amoeba, the splitting of the two cells
during division can take place in any plane.
Activity 7.3Activity 7.3Activity 7.3Activity 7.3Activity 7.3
/square6Observe a permanent slide of
Amoeba under a microscope.
/square6Similarly observe another
permanent slide of Amoeba
showing binary fission.
/square6Now, compare the observations of
both the slides.
However, some unicellular organisms
show somewhat more organisation of their
bodies, such as is seen in Leishmania (which
cause kala-azar), which have a whip-like
structure at one end of the cell. In such
organisms, binary fission occurs in a definite orientation in relation to
Figure 7.1(b)Figure 7.1(b)Figure 7.1(b)Figure 7.1(b)Figure 7.1(b)  Binary fission in Leishmania
  (a)         (b)          (c)          (d)            (e)                        (f)
```

### 3. pypdfium2 (Current)
```text
How do Organisms Reproduce? 115
Figure 7.1(a) Binary fission in Amoeba
Activity 7.2
7.2 MODES OF REPRODUCTION USED BY SINGLE
ORGANISMS
Activity 7.1
n Dissolve about 10 gm of sugar in 100 mL of water.
n Take 20 mL of this solution in a test tube and add a pinch of yeast
granules to it.
n Put a cotton plug on the mouth of the test tube and keep it in a
warm place.
n After 1 or 2 hours, put a small drop of yeast culture from the test
tube on a slide and cover it with a coverslip.
n Observe the slide under a microscope.
n Wet a slice of bread, and keep it in a cool, moist and dark place.
n Observe the surface of the slice with a magnifying glass.
n Record your observations for a week.
Compare and contrast the ways in which yeast grows in the first
case, and how mould grows in the second.
Having discussed the context in which reproductive processes work,
let us now examine how different organisms actually reproduce. The
modes by which various organisms reproduce depend on the body
design of the organisms.
7.2.1 Fission
For unicellular organisms, cell division, or fission, leads to the creation
of new individuals. Many different patterns of fission have been observed.
Many bacteria and protozoa simply split into two equal halves during
cell division. In organisms such as Amoeba, the splitting of the two cells
during division can take place in any plane.
Activity 7.3
n Observe a permanent slide of
Amoeba under a microscope.
n Similarly observe another
permanent slide of Amoeba
showing binary fission.
n Now, compare the observations of
both the slides.
However, some unicellular organisms
show somewhat more organisation of their
bodies, such as is seen in Leishmania (which
cause kala-azar), which have a whip-like
structure at one end of the cell. In such
organisms, binary fission occurs in a definite orientation in relation to
Figure 7.1(b) Binary fission in Leishmania
 (a) (b) (c) (d) (e) (f)
```

---

## Sample 11 [CHUNK_ID: chk_c5f706b46a5e23d4]
**Document:** STD-10/Std-10_Maths_EnglishMedium.pdf | **Page:** 37

### 1. PyMuPDF (fitz)
```text

	
22 –b
a 1
22 c
a 1
 –d
a 
C!
,- &3 " N  '
 &%

1
3
−
   >    
7'&(&%%&'
>

/		"#
##

7'

7&(
7&%%
7&' 
'7'8'&(8'&%%8'&'7H%&"(&''&'74
&%7'8&%&(8&%&%%8&%&'7&'&(#%%&'74
3
2
1
1
1
1
3
5
11
3
3
3
3
3
p⎛
⎞
⎛
⎞
⎛
⎞
⎛
⎞
−
=
× −
−
× −
−
× −
−
⎜
⎟
⎜
⎟
⎜
⎟
⎜
⎟
⎝
⎠
⎝
⎠
⎝
⎠
⎝
⎠

 7
1
5
11
2
2
–
3
–
0
9
9
3
3
3
−
+
−
=
+
=
/
'
&%
1
3
−
>'&(&%%&'
5
,α7'
β7&%γ7
1
3
−⋅
6
1
1
5
( 5)
3
( 1)
2
3
3
3
3
b
a
−−
−
⎛
⎞
α + β + γ =
+ −
+ −
=
−
=
=
=
⎜
⎟
⎝
⎠

1
1
1
11
3
( 1)
( 1)
3
3
1
3
3
3
3
c
a
−
⎛
⎞
⎛
⎞
αβ+ βγ +γα =
× −
+ −
× −
+ −
×
= −
+
−
=
=
⎜
⎟
⎜
⎟
⎝
⎠
⎝
⎠

1
( 3)
3
( 1)
1
3
3
d
a
−−
−
⎛
⎞
αβγ =
× −
× −
=
=
=
⎜
⎟
⎝
⎠

- 3		4
	

	
*
```

### 2. pypdf (Native)
```text
/G50/G50 /G77/G65 /G84/G72/G69/G77/G65 /G84/G73/G67/G83
/G97/G32/G43/G32/G98/G32/G43/G32/G103/G32/G61–b
a /G44
/G97/G98/G32/G43/G32/G98/G103/G32/G43/G32/G103/G97/G32/G61c
a /G44
/G97/G32 /G98/G32 /G103/G32/G61– d
a /G46
/G76/G101/G116/G32/G117/G115/G32/G99/G111/G110/G115/G105/G100/G101/G114/G32/G97/G110/G32/G101/G120/G97/G109/G112/G108/G101/G46
/G69/G120/G97/G109/G112/G108/G101/G32/G53/G42/G32/G58/G32/G86/G101/G114/G105/G102/G121/G32/G116/G104/G97/G116/G32/G51/G44/G32/G150/G49/G44/G321
3− /G32/G97/G114/G101/G32/G116/G104/G101/G32/G122/G101/G114/G111/G101/G115/G32/G111/G102/G32/G116/G104/G101/G32/G99/G117/G98/G105/G99/G32/G112/G111/G108/G121/G110/G111/G109/G105/G97/G108
/G112/G40/G120/G41/G32/G61/G32/G51/G120/G51/G32/G150/G32/G53/G120/G50/G32/G150/G32/G49/G49/G120/G32/G150/G32/G51/G44/G32/G97/G110/G100/G32/G116/G104/G101/G110/G32/G118/G101/G114/G105/G102/G121/G32/G116/G104/G101/G32/G114/G101/G108/G97/G116/G105/G111/G110/G115/G104/G105/G112/G32/G98/G101/G116/G119/G101/G101/G110/G32/G116/G104/G101/G32/G122/G101/G114/G111/G101/G115/G32/G97/G110/G100/G32/G116/G104/G101
/G99/G111/G101/G102/G102/G105/G99/G105/G101/G110/G116/G115/G46
/G83/G111/G108/G117/G116/G105/G111/G110/G32/G58/G32/G67/G111/G109/G112/G97/G114/G105/G110/G103/G32/G116/G104/G101/G32/G103/G105/G118/G101/G110/G32/G112/G111/G108/G121/G110/G111/G109/G105/G97/G108/G32/G119/G105/G116/G104/G32/G97/G120/G51/G32/G43/G32/G98/G120/G50/G32/G43/G32/G99/G120/G32/G43/G32/G100/G44/G32/G119/G101/G32/G103/G101/G116
/G97/G32/G61/G32/G51/G44/G32/G98/G32/G61/G32/G150/G32/G53/G44/G32/G99/G32/G61/G32/G150/G49/G49/G44/G32/G100/G32/G61/G32/G150/G32/G51/G46/G32/G70/G117/G114/G116/G104/G101/G114
/G112/G40/G51/G41/G32/G61/G32/G51/G32/G215/G32/G51/G51/G32/G150/G32/G40/G53/G32/G215/G32/G51/G50/G41/G32/G150/G32/G40/G49/G49/G32/G215/G32/G51/G41/G32/G150/G32/G51/G32/G61/G32/G56/G49/G32/G150/G32/G52/G53/G32/G150/G32/G51/G51/G32/G150/G32/G51/G32/G61/G32/G48/G44
/G112/G40/G150/G49/G41/G32/G61/G32/G51/G32/G215/G32/G40/G150/G49/G41/G51/G32/G150/G32/G53/G32/G215/G32/G40/G150/G49/G41/G50/G32/G150/G32/G49/G49/G32/G215/G32/G40/G150/G49/G41/G32/G150/G32/G51/G32/G61/G32/G150/G51/G32/G150/G32/G53/G32/G43/G32/G49/G49/G32/G150/G32/G51/G32/G61/G32/G48/G44
32
11 1 1351 1 333 3 3p⎛⎞ ⎛⎞ ⎛⎞ ⎛⎞− = ×− − ×− − ×− −⎜⎟ ⎜⎟ ⎜⎟ ⎜⎟⎝⎠ ⎝⎠ ⎝⎠ ⎝⎠ /G44
/G32/G32/G32/G32/G32/G32/G32/G32/G32/G32/G32/G32/G61/G32151 1 22–3 – 099 3 33−+ − = +=
/G84/G104/G101/G114/G101/G102/G111/G114/G101/G44/G32/G51/G44/G32/G150/G49/G32/G97/G110/G100/G321
3− /G32/G97/G114/G101/G32/G116/G104/G101/G32/G122/G101/G114/G111/G101/G115/G32/G111/G102/G32/G51/G120/G51/G32/G150/G32/G53/G120/G50/G32/G150/G32/G49/G49/G120/G32/G150/G32/G51/G46
/G83/G111/G44/G32/G119/G101/G32/G116/G97/G107/G101/G32α/G32/G61/G32/G51/G44/G32β/G32/G61/G32/G150/G49/G32/G97/G110/G100/G32γ/G32/G61/G321
3−⋅
/G78/G111/G119/G44
11 5 ( 5 )3( 1 ) 2 33 3 3
b
a
−− −⎛⎞α+β+γ = + − + − = − = = =⎜⎟⎝⎠
/G44
11 1 1 13( 1 ) ( 1 ) 3 3 1 33 33
c
a
−⎛⎞ ⎛⎞αβ+ βγ +γα = × − + − × − + − × = − + − = =⎜⎟ ⎜⎟⎝⎠ ⎝⎠
/G44
1( 3 )3( 1 ) 1 33
d
a
−− −⎛⎞αβγ = × − × − = = =⎜⎟⎝⎠
/G46
/G42/G78/G111/G116/G32/G102/G114/G111/G109/G32/G116/G104/G101/G32/G101/G120/G97/G109/G105/G110/G97/G116/G105/G111/G110/G32/G112/G111/G105/G110/G116/G32/G111/G102/G32/G118/G105/G101/G119/G46
```

### 3. pypdfium2 (Current)
```text
 	
22 –b
a 1
 2 2 
c
a 1
   – d
a 
C!
,- &3 " N '
 &%

1
3
−   >   
7'
&(&%%&'
>

/		" #
##

7'

7&(
7&%%
7&' 
'7'8'& (8'
&%%8'&'7H%&"(&''&'74

&%7'8&%
&(8&%&%%8&%&'7&'&(#%%&'74

32 11 1 1 3 5 11 3
33 3 3 p⎛⎞ ⎛⎞ ⎛⎞ ⎛⎞ ⎜⎟ ⎜⎟ ⎜⎟ ⎜⎟ − = ×− − ×− − ×− − ⎝⎠ ⎝⎠ ⎝⎠ ⎝⎠ 

 7
1 5 11 2 2 – 3– 0
99 3 33
− + −= + =
/
'
&%
1
3
− >'
&(&%%&'
5
,α7'
β7&%γ7
1
3
−⋅
6

1 1 5 ( 5) 3 ( 1) 2 3 33 3b
a
⎛⎞ −− − α +β+ γ= + − + − = − = = = ⎜⎟ ⎝⎠


1 1 1 11 3 ( 1) ( 1) 3 3 1 33 33c
a
⎛ ⎞⎛ ⎞ − αβ+ βγ +γα = × − + − × − + − × = − + − = = ⎜ ⎟⎜ ⎟ ⎝ ⎠⎝ ⎠


1 ( 3) 3 ( 1) 1 33d
a
⎛⎞ −− − αβγ = × − × − = = = ⎜⎟ ⎝⎠

- 3		4
	

	
*
```

---

## Sample 12 [CHUNK_ID: chk_6e1e893f80843d1c]
**Document:** STD-10/Std-10_Maths_EnglishMedium.pdf | **Page:** 35

### 1. PyMuPDF (fitz)
```text

	

>7α#β7
2
(Coefficient of
)
Coefficient of
b
x
a
x
−
−
=

>7αβ7
2
Constant term
Coefficient of
c
a
x
=

C!
,-" >1#)#%4

>
/		"9
#)#%47#$#(
5
#)#%4>#$74#(74

7&$
7&(/
>#)#%4&$&(6
>7
2
(7)
–(Coefficient of
) ,
–2
(–5)
– (7)
1
Coefficient of
x
x
−
+
=
=
=
>7
2
10
Constant term
( 2)
( 5)
10
1
Coefficient of x
−
× −
=
=
=
⋅
,-$" >&'
>
/		"&
7&
#
M
;
&'7 (
)(
)
3
3
x
x
−
+
5
&'>7
3 7 –
3⋅
/
>&'
3 
3
−
⋅
6
>7
2
(Coefficient of
),
3
3
0
Coefficient of
x
x
−
−
=
=
>7 (
)(
)
2
3
Constant term
3
3
– 3
1
Coefficient of x
−
−
=
=
=
⋅
```

### 2. pypdf (Native)
```text
/G50/G48 /G77/G65 /G84/G72/G69/G77/G65 /G84/G73/G67/G83
/G105/G46/G101/G46/G44/G115/G117/G109/G32/G111/G102/G32/G122/G101/G114/G111/G101/G115/G32/G61/G32α/G32/G43/G32β/G32/G61/G32 2
(Coefficient of )
Coefficient of
bx
a x
−−= /G44
/G112/G114/G111/G100/G117/G99/G116/G32/G111/G102/G32/G122/G101/G114/G111/G101/G115/G32/G61/G32αβ/G32/G61 2
Constant term
Coefficient of
c
a x
= /G46
/G76/G101/G116/G32/G117/G115/G32/G99/G111/G110/G115/G105/G100/G101/G114/G32/G115/G111/G109/G101/G32/G101/G120/G97/G109/G112/G108/G101/G115/G46
/G69/G120/G97/G109/G112/G108/G101/G32/G50/G32/G58/G32/G70/G105/G110/G100/G32/G116/G104/G101/G32/G122/G101/G114/G111/G101/G115/G32/G111/G102/G32/G116/G104/G101/G32/G113/G117/G97/G100/G114/G97/G116/G105/G99/G32/G112/G111/G108/G121/G110/G111/G109/G105/G97/G108/G32/G120/G50/G32/G43/G32/G55/G120/G32/G43/G32/G49/G48/G44/G32/G97/G110/G100/G32/G118/G101/G114/G105/G102/G121/G32/G116/G104/G101
/G114/G101/G108/G97/G116/G105/G111/G110/G115/G104/G105/G112/G32/G98/G101/G116/G119/G101/G101/G110/G32/G116/G104/G101/G32/G122/G101/G114/G111/G101/G115/G32/G97/G110/G100/G32/G116/G104/G101/G32/G99/G111/G101/G102/G102/G105/G99/G105/G101/G110/G116/G115/G46
/G83/G111/G108/G117/G116/G105/G111/G110/G32/G58/G32/G87/G101/G32/G104/G97/G118/G101
/G120/G50/G32/G43/G32/G55/G120/G32/G43/G32/G49/G48/G32/G61/G32/G40/G120/G32/G43/G32/G50/G41/G40/G120/G32/G43/G32/G53/G41
/G83/G111/G44/G32/G116/G104/G101/G32/G118/G97/G108/G117/G101/G32/G111/G102/G32/G120/G50/G32/G43/G32/G55/G120/G32/G43/G32/G49/G48/G32/G105/G115/G32/G122/G101/G114/G111/G32/G119/G104/G101/G110/G32/G120/G32/G43/G32/G50/G32/G61/G32/G48/G32/G111/G114/G32/G120/G32/G43/G32/G53/G32/G61/G32/G48/G44/G32/G105/G46/G101/G46/G44/G32/G119/G104/G101/G110/G32/G120/G32/G61/G32/G150/G32/G50/G32/G111/G114
/G120/G32/G61/G32/G150/G53/G46/G32/G84/G104/G101/G114/G101/G102/G111/G114/G101/G44/G32/G116/G104/G101/G32/G122/G101/G114/G111/G101/G115/G32/G111/G102/G32/G120/G50/G32/G43/G32/G55/G120/G32/G43/G32/G49/G48/G32/G97/G114/G101/G32/G150/G32/G50/G32/G97/G110/G100/G32/G150/G32/G53/G46/G32/G78/G111/G119/G44
/G115/G117/G109/G32/G111/G102/G32/G122/G101/G114/G111/G101/G115/G32/G612
(7) – (Coefficient of ) ,–2 ( –5 ) –( 7 ) 1 Coefficient of
x
x
−+= = =
/G112/G114/G111/G100/G117/G99/G116/G32/G111/G102/G32/G122/G101/G114/G111/G101/G115/G32/G612
10 Constant term(2 ) (5 ) 1 0 1 Coefficient of x
−× −= = = ⋅
/G69/G120/G97/G109/G112/G108/G101/G32/G51/G32/G58/G32/G70/G105/G110/G100/G32/G116/G104/G101/G32/G122/G101/G114/G111/G101/G115/G32/G111/G102/G32/G116/G104/G101/G32/G112/G111/G108/G121/G110/G111/G109/G105/G97/G108/G32/G120/G50/G32/G150/G32/G51/G32/G97/G110/G100/G32/G118/G101/G114/G105/G102/G121/G32/G116/G104/G101/G32/G114/G101/G108/G97/G116/G105/G111/G110/G115/G104/G105/G112
/G98/G101/G116/G119/G101/G101/G110/G32/G116/G104/G101/G32/G122/G101/G114/G111/G101/G115/G32/G97/G110/G100/G32/G116/G104/G101/G32/G99/G111/G101/G102/G102/G105/G99/G105/G101/G110/G116/G115/G46
/G83/G111/G108/G117/G116/G105/G111/G110/G32/G58/G32/G82/G101/G99/G97/G108/G108/G32/G116/G104/G101/G32/G105/G100/G101/G110/G116/G105/G116/G121/G32/G97/G50/G32/G150/G32/G98/G50/G32/G61/G32/G40/G97/G32/G150/G32/G98/G41/G40/G97/G32/G43/G32/G98/G41/G46/G32/G85/G115/G105/G110/G103/G32/G105/G116/G44/G32/G119/G101/G32/G99/G97/G110/G32/G119/G114/G105/G116/G101/G58
/G120/G50/G32/G150/G32/G51/G32/G61() ()33xx−+
/G83/G111/G44/G32/G116/G104/G101/G32/G118/G97/G108/G117/G101/G32/G111/G102/G32/G120/G50/G32/G150/G32/G51/G32/G105/G115/G32/G122/G101/G114/G111/G32/G119/G104/G101/G110/G32/G120/G32/G61/G323/G32/G111/G114/G32/G120/G32/G61/G32–3 ⋅
/G84/G104/G101/G114/G101/G102/G111/G114/G101/G44/G32/G116/G104/G101/G32/G122/G101/G114/G111/G101/G115/G32/G111/G102/G32/G120/G50/G32/G150/G32/G51/G32/G97/G114/G101/G323/G32/G97/G110/G100/G323−⋅
/G78/G111/G119/G44
/G115/G117/G109/G32/G111/G102/G32/G122/G101/G114/G111/G101/G115/G32/G612
(Coefficient of ) ,33 0
Coefficient of
x
x
−−= =
/G112/G114/G111/G100/G117/G99/G116/G32/G111/G102/G32/G122/G101/G114/G111/G101/G115/G32/G61() () 2
3C o n s t a n t t e r m33 – 3 1 Coefficient of x
−−= = = ⋅
```

### 3. pypdfium2 (Current)
```text
 	

 >7α#β7 2
(Coefficient of )
Coefficient of
bx
a x
− −= 

>7αβ7 2
Constant term
Coefficient of
c
a x = 
C!
,-" >1
#)#%4

>
/		" 9

#)#%47#$#(
5

#)#%4>#$74#(74

7&$
7&(/
>#)#%4&$&(6

>7 2
(7) – (Coefficient of ) – 2 (–5) – (7) , 1 Coefficient of
x
x
− += = =
>7 2
10 Constant term ( 2) ( 5) 10 1 Coefficient of x
− ×− = = = ⋅
,-$ " >&' 
>
/		" 
&
7&
#
M
;
&'7 () xx −+ 33 ()
5
&'>7 3 7 –3⋅
/
>&' 3  −⋅ 3
6

>7
2
(Coefficient of ) 3 30 ,
Coefficient of
x
x
− − ==
>7 ()() 2
3 Constant term 3 3 –3
1 Coefficient of x
− − === ⋅
```

---

## Sample 13 [CHUNK_ID: chk_32d384f8599be76c]
**Document:** STD-10/Std-10_Maths_EnglishMedium.pdf | **Page:** 96

### 1. PyMuPDF (fitz)
```text
	
	/
 		
!,"!<"!/"=
AD
DB C AE
EC
	
!5
	
7)7,"& )
	
	=

'7  
(7
(::
:::7:C::C::C
::C::
8
   7 
( 
7CC
CC %::
!5.,,"
3
1
1
AB
B B C
1
1
AC
C C
!$2 1
4 "
::
:EE :
!,"
8
%:::=
2
2
AB
B B C
2
2
AC
C C 
2
3
⎛
⎞
=
⎜
⎟
⎝
⎠ :EE:
!<"
3
3
AB
B B C
3
3
AC
C C 
3
2
⎛
⎞
=
⎜
⎟
⎝
⎠ :EE:
!/"
4
4
AB
B B C
4
4
AC
C C 
4
1
⎛
⎞
=
⎜
⎟
⎝
⎠ :EE:
!?"
5
!,"!<"!/"!?"		


7			

(
	2
77$


 	
	
 
.,

```

### 2. pypdf (Native)
```text
/G84/G82/G73/G65/G78/G71/G76/G69/G83 /G56/G49
/G84/G104/G101/G114/G101/G102/G111/G114/G101/G44/G32/G102/G114/G111/G109/G32/G40/G49/G41/G44/G32/G40/G50/G41/G32/G97/G110/G100/G32/G40/G51/G41/G44/G32/G119/G101/G32/G104/G97/G118/G101/G32/G58
AD
DB/G32/G61AE
EC
/G73/G115/G32/G116/G104/G101/G32/G99/G111/G110/G118/G101/G114/G115/G101/G32/G111/G102/G32/G116/G104/G105/G115/G32/G116/G104/G101/G111/G114/G101/G109/G32/G97/G108/G115/G111/G32/G116/G114/G117/G101/G32/G40/G70/G111/G114/G32/G116/G104/G101/G32/G109/G101/G97/G110/G105/G110/G103/G32/G111/G102/G32/G99/G111/G110/G118/G101/G114/G115/G101/G44/G32/G115/G101/G101
/G65/G112/G112/G101/G110/G100/G105/G120/G32/G65/G49/G41/G63/G32/G84/G111/G32/G101/G120/G97/G109/G105/G110/G101/G32/G116/G104/G105/G115/G44/G32/G108/G101/G116/G32/G117/G115/G32/G112/G101/G114/G102/G111/G114/G109/G32/G116/G104/G101/G32/G102/G111/G108/G108/G111/G119/G105/G110/G103/G32/G97/G99/G116/G105/G118/G105/G116/G121/G58
/G65/G99/G116/G105/G118/G105/G116/G121/G32/G51/G32/G58/G32/G32/G68/G114/G97/G119/G32/G97/G110/G32/G97/G110/G103/G108/G101/G32/G88/G65/G89/G32/G111/G110/G32/G121/G111/G117/G114
/G110/G111/G116/G101/G98/G111/G111/G107/G32/G97/G110/G100/G32
/G111/G110/G32/G114/G97/G121/G32/G65/G88/G44/G32/G109/G97/G114/G107/G32/G112/G111/G105/G110/G116/G115/G32/G66/G49/G44/G32/G66/G50/G44
/G66/G51/G44/G32/G66/G52/G32/G97/G110/G100/G32/G66/G32/G115/G117/G99/G104/G32/G116/G104/G97/G116/G32/G65/G66/G49/G32/G61/G32/G66/G49/G66/G50/G32/G61/G32/G66/G50/G66/G51/G32/G61
/G66/G51/G66/G52/G32/G61/G32/G66/G52/G66/G46
/G83/G105/G109/G105/G108/G97/G114/G108/G121/G44/G32/G111/G110/G32/G114/G97/G121/G32/G65/G89/G44/G32/G109/G97/G114/G107/G32/G112/G111/G105/G110/G116/G115
/G67/G49/G44/G32/G67/G50/G44/G32/G67/G51/G44/G32/G67/G52/G32/G97/G110/G100/G32/G67/G32/G115/G117/G99/G104/G32/G116/G104/G97/G116/G32/G65/G67/G49/G32/G61/G32/G67/G49/G67/G50/G32/G61
/G67/G50/G67/G51/G32/G61/G32/G67/G51/G67/G52/G32/G61/G32/G67/G52/G67/G46/G32/G84/G104/G101/G110/G32/G106/G111/G105/G110/G32/G66/G49/G67/G49/G32/G97/G110/G100/G32/G66/G67
/G40/G115/G101/G101/G32/G70/G105/G103/G46/G32/G54/G46/G49/G49/G41/G46
/G78/G111/G116/G101/G32/G116/G104/G97/G116
1
1
AB
BB /G32/G61
1
1
AC
CC /G40/G69/G97/G99/G104/G32/G101/G113/G117/G97/G108/G32/G116/G111/G321
4/G41
/G89/G111/G117/G32/G99/G97/G110/G32/G97/G108/G115/G111/G32/G115/G101/G101/G32/G116/G104/G97/G116/G32/G108/G105/G110/G101/G115/G32/G66/G49/G67/G49/G32/G97/G110/G100/G32/G66/G67/G32/G97/G114/G101/G32/G112/G97/G114/G97/G108/G108/G101/G108/G32/G116/G111/G32/G101/G97/G99/G104/G32/G111/G116/G104/G101/G114/G44/G32/G105/G46/G101/G46/G44
/G66/G49/G67/G49/G32/G124/G124/G66/G67 /G40/G49/G41
/G83/G105/G109/G105/G108/G97/G114/G108/G121/G44/G32/G98/G121/G32/G106/G111/G105/G110/G105/G110/G103/G32/G66/G50/G67/G50/G44/G32/G66/G51/G67/G51/G32/G97/G110/G100/G32/G66/G52/G67/G52/G44/G32/G121/G111/G117/G32/G99/G97/G110/G32/G115/G101/G101/G32/G116/G104/G97/G116/G58
2
2
AB
BB /G32/G612
2
AC
CC /G32
2
3
⎛⎞=⎜⎟⎝⎠ /G97/G110/G100 /G66/G50/G67/G50/G32/G124/G124/G32/G66/G67/G40/G50/G41
3
3
AB
BB /G32/G61
3
3
AC
CC /G32
3
2
⎛⎞=⎜⎟⎝⎠ /G97/G110/G100 /G66/G51/G67/G51/G32/G124/G124/G32/G66/G67/G40/G51/G41
4
4
AB
BB /G32/G614
4
AC
CC /G32
4
1
⎛⎞=⎜⎟⎝⎠ /G97/G110/G100 /G66/G52/G67/G52/G32/G124/G124/G32/G66/G67/G40/G52/G41
/G70/G114/G111/G109/G32/G40/G49/G41/G44/G32/G40/G50/G41/G44/G32/G40/G51/G41/G32/G97/G110/G100/G32/G40/G52/G41/G44/G32/G105/G116/G32/G99/G97/G110/G32/G98/G101/G32/G111/G98/G115/G101/G114/G118/G101/G100/G32/G116/G104/G97/G116/G32/G105/G102/G32/G97/G32/G108/G105/G110/G101/G32/G100/G105/G118/G105/G100/G101/G115/G32/G116/G119/G111/G32/G115/G105/G100/G101/G115/G32/G111/G102/G32/G97
/G116/G114/G105/G97/G110/G103/G108/G101/G32/G105/G110/G32/G116/G104/G101/G32/G115/G97/G109/G101/G32/G114/G97/G116/G105/G111/G44/G32/G116/G104/G101/G110/G32/G116/G104/G101/G32/G108/G105/G110/G101/G32/G105/G115/G32/G112/G97/G114/G97/G108/G108/G101/G108/G32/G116/G111/G32/G116/G104/G101/G32/G116/G104/G105/G114/G100/G32/G115/G105/G100/G101/G46
/G89/G111/G117/G32/G99/G97/G110/G32/G114/G101/G112/G101/G97/G116/G32/G116/G104/G105/G115/G32/G97/G99/G116/G105/G118/G105/G116/G121/G32/G98/G121/G32/G100/G114/G97/G119/G105/G110/G103/G32/G97/G110/G121/G32/G97/G110/G103/G108/G101/G32/G88/G65/G89/G32/G111/G102/G32/G100/G105/G102/G102/G101/G114/G101/G110/G116/G32/G109/G101/G97/G115/G117/G114/G101/G32/G97/G110/G100
/G116/G97/G107/G105/G110/G103/G32/G97/G110/G121/G32/G32/G110/G117/G109/G98/G101/G114/G32/G111/G102/G32/G101/G113/G117/G97/G108/G32/G112/G97/G114/G116/G115/G32/G111/G110/G32/G97/G114/G109/G115/G32/G65/G88/G32/G97/G110/G100/G32/G65/G89/G32/G46/G32/G69/G97/G99/G104/G32/G116/G105/G109/G101/G44/G32/G121/G111/G117/G32/G119/G105/G108/G108/G32/G97/G114/G114/G105/G118/G101/G32/G97/G116
/G116/G104/G101/G32/G115/G97/G109/G101/G32/G114/G101/G115/G117/G108/G116/G46/G32/G84/G104/G117/G115/G44/G32/G119/G101/G32/G111/G98/G116/G97/G105/G110/G32/G116/G104/G101/G32/G102/G111/G108/G108/G111/G119/G105/G110/G103/G32/G116/G104/G101/G111/G114/G101/G109/G44/G32/G119/G104/G105/G99/G104/G32/G105/G115/G32/G116/G104/G101/G32/G99/G111/G110/G118/G101/G114/G115/G101/G32/G111/G102
/G84/G104/G101/G111/G114/G101/G109/G32/G54/G46/G49/G46
/G70/G105/G103/G46/G32/G54/G46/G49/G49
```

### 3. pypdfium2 (Current)
```text
	 	/
 		
!,"!<"!/"=
AD
DB C
AE
EC
  	
  !5
 	  
7)7,"& )
	
	=
 
   '   7  
(7
(:
:
::: 7: C:: C::C
:
: C::
8
   7 
( 

 7CC

 C C %: :
!5.,,"
3 1
1
AB
BB C
1
1
AC
CC !$2
1
4 "
:
:
:
 EE : !,"
8
%:::=
2
2
AB
BB
C
2
2
AC
CC
2
3
⎛⎞ ⎜⎟ =
⎝⎠  :
EE: !<"
3
3
AB
BB C
3
3
AC
CC
3
2
⎛⎞ ⎜⎟ =
⎝⎠  :
EE: !/"
4
4
AB
BB
C
4
4
AC
CC
4
1
⎛⎞ ⎜⎟ =
⎝⎠  :
EE: !?"
5
!,"!<"!/"!?"		


7			

(
	2
77$


   	
	
 
.,
 
```

---

## Sample 14 [CHUNK_ID: chk_0035d9f2beb76466]
**Document:** STD-10/Std-10_Maths_EnglishMedium.pdf | **Page:** 254

### 1. PyMuPDF (fitz)
```text
	
		


 	



	
			
	
	




				



				
	
 	!"
#$
$			
	

			
	%&	
		
		
	
%&	
		
			
	%
&	
			
 $	
	
		'		
			
 %
 	

$	
'		
'%
(	
$	
		
$

$		
")*+	
		
		
		
,			
		
	'	
	'
	
	'			

 	
	'$	,$			
-		
	(	
	
	
			
			
			
,$	
				
	
		
	$
	./$

	
	'	'	

 $
	
	''		0
12 3'	
$	
	
	

12 4		'	
	
4	
	
	
12 4		'	
		$4	
	
	
12 5	'	
	
	
	
		
```

### 2. pypdf (Native)
```text
/G77/G65 /G84/G72/G69/G77/G65 /G84/G73/G67/G65/G76/G32/G77/G79/G68/G69/G76/G76/G73/G78/G71 /G50/G51/G57
/G65/G50
/G65/G50/G46/G49 /G73/G110/G116/G114/G111/G100/G117/G99/G116/G105/G111/G110
/G108/G65/G110/G32/G97/G100/G117/G108/G116/G32/G104/G117/G109/G97/G110/G32/G98/G111/G100/G121/G32/G99/G111/G110/G116/G97/G105/G110/G115/G32/G97/G112/G112/G114/G111/G120/G105/G109/G97/G116/G101/G108/G121/G32/G49/G44/G53/G48/G44/G48/G48/G48/G32/G107/G109/G32/G111/G102/G32/G97/G114/G116/G101/G114/G105/G101/G115/G32/G97/G110/G100/G32/G118/G101/G105/G110/G115
/G116/G104/G97/G116/G32/G99/G97/G114/G114/G121/G32/G98/G108/G111/G111/G100/G46
/G108/G84/G104/G101/G32/G104/G117/G109/G97/G110/G32/G104/G101/G97/G114/G116/G32/G112/G117/G109/G112/G115/G32/G53/G32/G116/G111/G32/G54/G32/G108/G105/G116/G114/G101/G115/G32/G111/G102/G32/G98/G108/G111/G111/G100/G32/G105/G110/G32/G116/G104/G101/G32/G98/G111/G100/G121/G32/G101/G118/G101/G114/G121/G32/G54/G48/G32/G115/G101/G99/G111/G110/G100/G115/G46
/G108/G84/G104/G101/G32/G116/G101/G109/G112/G101/G114/G97/G116/G117/G114/G101/G32/G97/G116/G32/G116/G104/G101/G32/G115/G117/G114/G102/G97/G99/G101/G32/G111/G102/G32/G116/G104/G101/G32/G83/G117/G110/G32/G105/G115/G32/G97/G98/G111/G117/G116/G32/G54/G44/G48/G48/G48/G176/G32/G67/G46
/G72/G97/G118/G101/G32/G121/G111/G117/G32/G101/G118/G101/G114/G32/G119/G111/G110/G100/G101/G114/G101/G100/G32/G104/G111/G119/G32/G111/G117/G114/G32/G115/G99/G105/G101/G110/G116/G105/G115/G116/G115/G32/G97/G110/G100/G32/G109/G97/G116/G104/G101/G109/G97/G116/G105/G99/G105/G97/G110/G115/G32/G99/G111/G117/G108/G100/G32/G112/G111/G115/G115/G105/G98/G108/G121
/G104/G97/G118/G101/G32/G101/G115/G116/G105/G109/G97/G116/G101/G100/G32/G116/G104/G101/G115/G101/G32/G114/G101/G115/G117/G108/G116/G115/G63/G32/G68/G105/G100/G32/G116/G104/G101/G121/G32/G112/G117/G108/G108/G32/G111/G117/G116/G32/G116/G104/G101/G32/G118/G101/G105/G110/G115/G32/G97/G110/G100/G32/G97/G114/G116/G101/G114/G105/G101/G115/G32/G102/G114/G111/G109/G32/G115/G111/G109/G101/G32/G97/G100/G117/G108/G116
/G100/G101/G97/G100/G32/G98/G111/G100/G105/G101/G115/G32/G97/G110/G100/G32/G109/G101/G97/G115/G117/G114/G101/G32/G116/G104/G101/G109/G63/G32/G68/G105/G100/G32/G116/G104/G101/G121/G32/G100/G114/G97/G105/G110/G32/G111/G117/G116/G32/G116/G104/G101/G32/G98/G108/G111/G111/G100/G32/G116/G111/G32/G97/G114/G114/G105/G118/G101/G32/G97/G116/G32/G116/G104/G101/G115/G101/G32/G114/G101/G115/G117/G108/G116/G115/G63
/G68/G105/G100/G32/G116/G104/G101/G121/G32/G116/G114/G97/G118/G101/G108/G32/G116/G111/G32/G116/G104/G101/G32/G83/G117/G110/G32/G119/G105/G116/G104/G32/G97/G32/G116/G104/G101/G114/G109/G111/G109/G101/G116/G101/G114/G32/G116/G111/G32/G103/G101/G116/G32/G116/G104/G101/G32/G116/G101/G109/G112/G101/G114/G97/G116/G117/G114/G101/G32/G111/G102/G32/G116/G104/G101/G32/G83/G117/G110/G63
/G83/G117/G114/G101/G108/G121/G32/G110/G111/G116/G46/G32/G84/G104/G101/G110/G32/G104/G111/G119/G32/G100/G105/G100/G32/G116/G104/G101/G121/G32/G103/G101/G116/G32/G116/G104/G101/G115/G101/G32/G102/G105/G103/G117/G114/G101/G115/G63
/G87/G101/G108/G108/G44/G32/G116/G104/G101/G32/G97/G110/G115/G119/G101/G114/G32/G108/G105/G101/G115/G32/G105/G110/G32/G109/G97/G116/G104/G101/G109/G97/G116/G105/G99/G97/G108/G32/G109/G111/G100/G101/G108/G108/G105/G110/G103/G44/G32/G119/G104/G105/G99/G104/G32/G119/G101/G32/G105/G110/G116/G114/G111/G100/G117/G99/G101/G100/G32/G116/G111/G32/G121/G111/G117
/G105/G110/G32/G67/G108/G97/G115/G115/G32/G73/G88/G46/G32/G82/G101/G99/G97/G108/G108/G32/G116/G104/G97/G116/G32/G97/G32/G109/G97/G116/G104/G101/G109/G97/G116/G105/G99/G97/G108/G32/G109/G111/G100/G101/G108/G32/G105/G115/G32/G97/G32/G109/G97/G116/G104/G101/G109/G97/G116/G105/G99/G97/G108/G32/G100/G101/G115/G99/G114/G105/G112/G116/G105/G111/G110/G32/G111/G102/G32/G115/G111/G109/G101
/G114/G101/G97/G108/G45/G108/G105/G102/G101/G32/G115/G105/G116/G117/G97/G116/G105/G111/G110/G46/G32/G65/G108/G115/G111/G44/G32/G114/G101/G99/G97/G108/G108/G32/G116/G104/G97/G116/G32/G109/G97/G116/G104/G101/G109/G97/G116/G105/G99/G97/G108/G32/G109/G111/G100/G101/G108/G108/G105/G110/G103/G32/G105/G115/G32/G116/G104/G101/G32/G112/G114/G111/G99/G101/G115/G115/G32/G111/G102/G32/G99/G114/G101/G97/G116/G105/G110/G103/G32/G97
/G109/G97/G116/G104/G101/G109/G97/G116/G105/G99/G97/G108/G32/G109/G111/G100/G101/G108/G32/G111/G102/G32/G97/G32/G112/G114/G111/G98/G108/G101/G109/G44/G32/G97/G110/G100/G32/G117/G115/G105/G110/G103/G32/G105/G116/G32/G116/G111/G32/G97/G110/G97/G108/G121/G115/G101/G32/G97/G110/G100/G32/G115/G111/G108/G118/G101/G32/G116/G104/G101/G32/G112/G114/G111/G98/G108/G101/G109/G46
/G83/G111/G44/G32/G105/G110/G32/G109/G97/G116/G104/G101/G109/G97/G116/G105/G99/G97/G108/G32/G109/G111/G100/G101/G108/G108/G105/G110/G103/G44/G32/G119/G101/G32/G116/G97/G107/G101/G32/G97/G32/G114/G101/G97/G108/G45/G119/G111/G114/G108/G100/G32/G112/G114/G111/G98/G108/G101/G109/G32/G97/G110/G100/G32/G99/G111/G110/G118/G101/G114/G116/G32/G105/G116/G32/G116/G111/G32/G97/G110
/G101/G113/G117/G105/G118/G97/G108/G101/G110/G116/G32/G109/G97/G116/G104/G101/G109/G97/G116/G105/G99/G97/G108/G32/G112/G114/G111/G98/G108/G101/G109/G46/G32/G87/G101/G32/G116/G104/G101/G110/G32/G115/G111/G108/G118/G101/G32/G116/G104/G101/G32/G109/G97/G116/G104/G101/G109/G97/G116/G105/G99/G97/G108/G32/G112/G114/G111/G98/G108/G101/G109/G44/G32/G97/G110/G100/G32/G105/G110/G116/G101/G114/G112/G114/G101/G116
/G105/G116/G115/G32/G115/G111/G108/G117/G116/G105/G111/G110/G32/G105/G110/G32/G116/G104/G101/G32/G115/G105/G116/G117/G97/G116/G105/G111/G110/G32/G111/G102/G32/G116/G104/G101/G32/G114/G101/G97/G108/G45/G119/G111/G114/G108/G100/G32/G112/G114/G111/G98/G108/G101/G109/G46/G32/G65/G110/G100/G32/G116/G104/G101/G110/G44/G32/G105/G116/G32/G105/G115/G32/G105/G109/G112/G111/G114/G116/G97/G110/G116/G32/G116/G111/G32/G115/G101/G101
/G116/G104/G97/G116/G32/G116/G104/G101/G32/G115/G111/G108/G117/G116/G105/G111/G110/G44/G32/G119/G101/G32/G104/G97/G118/G101/G32/G111/G98/G116/G97/G105/G110/G101/G100/G44/G32/G145/G109/G97/G107/G101/G115/G32/G115/G101/G110/G115/G101/G146/G44/G32/G119/G104/G105/G99/G104/G32/G105/G115/G32/G116/G104/G101/G32/G115/G116/G97/G103/G101/G32/G111/G102/G32/G118/G97/G108/G105/G100/G97/G116/G105/G110/G103/G32/G116/G104/G101
/G109/G111/G100/G101/G108/G46/G32/G83/G111/G109/G101/G32/G101/G120/G97/G109/G112/G108/G101/G115/G44/G32/G119/G104/G101/G114/G101/G32/G109/G97/G116/G104/G101/G109/G97/G116/G105/G99/G97/G108/G32/G109/G111/G100/G101/G108/G108/G105/G110/G103/G32/G105/G115/G32/G111/G102/G32/G103/G114/G101/G97/G116/G32/G105/G109/G112/G111/G114/G116/G97/G110/G99/G101/G44/G32/G97/G114/G101/G58
/G40/G105/G41 /G70/G105/G110/G100/G105/G110/G103/G32/G116/G104/G101/G32/G119/G105/G100/G116/G104/G32/G97/G110/G100/G32/G100/G101/G112/G116/G104/G32/G111/G102/G32/G97/G32/G114/G105/G118/G101/G114/G32/G97/G116/G32/G97/G110/G32/G117/G110/G114/G101/G97/G99/G104/G97/G98/G108/G101/G32/G112/G108/G97/G99/G101/G46
/G40/G105/G105/G41 /G69/G115/G116/G105/G109/G97/G116/G105/G110/G103/G32/G116/G104/G101/G32/G109/G97/G115/G115/G32/G111/G102/G32/G116/G104/G101/G32/G69/G97/G114/G116/G104/G32/G97/G110/G100/G32/G111/G116/G104/G101/G114/G32/G112/G108/G97/G110/G101/G116/G115/G46
/G40/G105/G105/G105/G41/G69/G115/G116/G105/G109/G97/G116/G105/G110/G103/G32/G116/G104/G101/G32/G100/G105/G115/G116/G97/G110/G99/G101/G32/G98/G101/G116/G119/G101/G101/G110/G32/G69/G97/G114/G116/G104/G32/G97/G110/G100/G32/G97/G110/G121/G32/G111/G116/G104/G101/G114/G32/G112/G108/G97/G110/G101/G116/G46
/G40/G105/G118/G41/G80/G114/G101/G100/G105/G99/G116/G105/G110/G103/G32/G116/G104/G101/G32/G97/G114/G114/G114/G105/G118/G97/G108/G32/G111/G102/G32/G116/G104/G101/G32/G109/G111/G110/G115/G111/G111/G110/G32/G105/G110/G32/G97/G32/G99/G111/G117/G110/G116/G114/G121/G46
/G77/G65/G84/G72/G69/G77/G65/G84/G73/G67/G65/G76/G32/G77/G79/G68/G69/G76/G76/G73/G78/G71
```

### 3. pypdfium2 (Current)
```text
	
		 

 	


 	
			
	
	
 


				

 
				
	
 	!"
#$
$			
	

			
	%&	
		
		
	
%&	
		
			
	%
&	
			
 $	
	
		'		
			
 %
 	

$	
'		
'%
(	
$	
		
$

$		
")*+	
		
		
		
,			
		
	'	
	'
	
	'			

 	
	'$	,$			
-		
	(	
	
	
			
			
			
,$	
				
	
		
	$
	./$

	
	'	'	

 $
	
	''		0
12 3'	
$	
	
	

12 4		'	
	
4	
	
	
12 4		'	
		$4	
	
	
12 5	'	
	
	
	
		
```

---

## Sample 15 [CHUNK_ID: chk_5e85035fb5eb5d68]
**Document:** STD-10/Std-10_Maths_EnglishMedium.pdf | **Page:** 268

### 1. PyMuPDF (fitz)
```text
8
		9
	

 	

 &*,	"  	( 	 	5
 D'*,	"  	 2
2
,
3
3
 E4	"  	 3
3
2
±

 			F	 2 6
 			
 C2		$		
  
 C2		$		
 	

 C2	$	$	$	2	2	2	+ "	*	8;	*	*4.	44(0	"		 /*(	/1	*((0		
	)"4(0	"2
  2	? ,	*"	?$	
2
3V
3
,
V,
4
4
⎛
⎞
⎜
⎟
⎝
⎠

 C2	$	$	$	2	2	2	+ "	*	8;2
  2	8 	*"		
2
3
8
8
8
,
,
,
1
10000 1
10000 1
100
100
100
⎛
⎞
⎛
⎞
⎛
⎞
+
+
+
⎜
⎟
⎜
⎟
⎜
⎟
⎝
⎠
⎝
⎠
⎝
⎠


 $	$	$	
 #	$	#	$	#	$	#	
 $	$	#	$	#	

1
1
,
–1,
0,
2
2
−
 #	2$	#	2	$	#	2$	#	2

 
		$ 		#	
 
		#	$ 		

1
4
,
3
3
a
d
=
=
 
		2$ 		2

  
 C2	
1
9 ,
; 4,
5
2
2
d =
 C2			#		#	2$	#2$	#	2
 C2			 $	$	
 C2			 2 	3
4 2 , 3
5 2 , 3
6 2
+
+
+
  
 C2			#	 #	$	#	$	#	
 C2	
1
1
1
,
,
0;
2
2
2
d =
−
−
−
5  
5 C2			
	
$	
$	
5  
5 C2			
2; 	 50 ,
72 ,
98
5  
5  
5 C2				$	$	
 	

 
		
 		
 
		
 		
 
		2
```

### 2. pypdf (Native)
```text
/G65/G78/G83/G87/G69/G82/G83/G47/G72/G73/G78/G84/G83 /G50/G53/G51
/G69/G88/G69/G82/G67/G73/G83/G69 /G52/G46/G51
/G49/G46/G40/G105/G41 /G82/G101/G97/G108/G32/G114/G111/G111/G116/G115/G32/G100/G111/G32/G110/G111/G116/G32/G101/G120/G105/G115/G116/G40/G105/G105/G41/G69/G113/G117/G97/G108/G32/G114/G111/G111/G116/G115/G59/G3222,
33
/G40/G105/G105/G105/G41/G68/G105/G115/G116/G105/G110/G99/G116/G32/G114/G111/G111/G116/G115/G59/G3233
2
±
/G50/G46/G40/G105/G41/G107/G32/G61/G32/G177/G3226 /G40/G105/G105/G41/G107/G32/G61/G32/G54
/G51/G46/G89/G101/G115/G46/G32/G52/G48/G32/G109/G44/G32/G50/G48/G32/G109/G52/G46/G78/G111 /G53/G46/G89/G101/G115/G46/G32/G50/G48/G32/G109/G44/G32/G50/G48/G32/G109
/G69/G88/G69/G82/G67/G73/G83/G69 /G53/G46/G49
/G49/G46/G40/G105/G41 /G89/G101/G115/G46/G32/G49/G53/G44/G32/G50/G51/G44/G32/G51/G49/G44/G32/G46/G32/G46/G32/G46/G32/G102/G111/G114/G109/G115/G32/G97/G110/G32/G65/G80/G32/G97/G115/G32/G101/G97/G99/G104/G32/G115/G117/G99/G99/G101/G101/G100/G105/G110/G103/G32/G116/G101/G114/G109/G32/G105/G115/G32/G111/G98/G116/G97/G105/G110/G101/G100/G32/G98/G121/G32/G97/G100/G100/G105/G110/G103/G32/G56/G32/G105/G110
/G105/G116/G115/G32/G112/G114/G101/G99/G101/G100/G105/G110/G103/G32/G116/G101/G114/G109/G46
/G40/G105/G105/G41 /G78/G111/G46/G32/G86/G111/G108/G117/G109/G101/G115/G32/G97/G114/G101/G32/G86/G44/G32
2
3V 3, V,44
⎛⎞
⎜⎟⎝⎠
/G34/G40/G105/G105/G105/G41 /G89/G101/G115/G46/G32/G49/G53/G48/G44/G32/G50/G48/G48/G44/G32/G50/G53/G48/G44/G32/G46/G32/G46/G32/G46/G32/G102/G111/G114/G109/G32/G97/G110/G32/G65/G80/G46
/G40/G105/G118/G41 /G78/G111/G46/G32/G65/G109/G111/G117/G110/G116/G115/G32/G97/G114/G101/G32/G49/G48/G48/G48/G48/G32
23
88 8,, ,1 10000 1 10000 1100 100 100
⎛⎞ ⎛⎞ ⎛⎞++ +⎜⎟ ⎜⎟ ⎜⎟⎝⎠ ⎝⎠ ⎝⎠
/G34
/G50/G46/G40/G105/G41 /G49/G48/G44/G32/G50/G48/G44/G32/G51/G48/G44/G32/G52/G48/G40/G105/G105/G41 /G150/G32/G50/G44/G32/G150/G32/G50/G44/G32/G150/G32/G50/G44/G32/G150/G32/G50 /G40/G105/G105/G105/G41 /G52/G44/G32/G49/G44/G32/G150/G32/G50/G44/G32/G150/G32/G53
/G40/G105/G118/G4111,–1, 0,22− /G40/G118/G41 /G150/G32/G49/G46/G50/G53/G44/G32/G150/G32/G49/G46/G32/G53/G48/G44/G32/G150/G32/G49/G46/G55/G53/G44/G32/G150/G32/G50/G46/G48
/G51/G46/G40/G105/G41/G97/G32/G61/G32/G51/G44/G100/G32/G61/G32/G150/G32/G50/G40/G105/G105/G41/G97/G32/G61/G32/G150/G32/G53/G44/G100/G32/G61/G32/G52
/G40/G105/G105/G105/G4114,
33ad== /G40/G105/G118/G41/G97/G32/G61/G32/G48/G46/G54/G44/G100/G32/G61/G32/G49/G46/G49
/G52/G46/G40/G105/G41 /G78/G111/G40/G105/G105/G41 /G89/G101/G115/G46/G3219 ,;4 , 522d =
/G40/G105/G105/G105/G41 /G89/G101/G115/G46/G32/G100/G32/G61/G32/G150/G32/G50/G59/G32/G150/G32/G57/G46/G50/G44/G32/G150/G49/G49/G46/G50/G44/G32/G150/G32/G49/G51/G46/G50/G40/G105/G118/G41 /G89/G101/G115/G46/G32/G100/G32/G61/G32/G52/G59 /G54/G44/G32/G49/G48/G44/G32/G49/G52
/G40/G118/G41 /G89/G101/G115/G46/G32/G100/G32/G61/G322/G59/G323 4 2, 3 5 2, 3 6 2+++ /G40/G118/G105/G41 /G78/G111
/G40/G118/G105/G105/G41 /G89/G101/G115/G46/G32/G100/G32/G61/G32/G150/G32/G52/G59 /G150/G32/G49/G54/G44/G32/G150/G32/G50/G48/G44/G32/G150/G32/G50/G52 /G40/G118/G105/G105/G105/G41 /G89/G101/G115/G46/G32111 ,,0; 222d =−−−
/G40/G105/G120/G41 /G78/G111/G40/G120/G41 /G89/G101/G115/G46/G32/G100/G32/G61/G32/G97/G59/G32/G53/G97/G44/G32/G54/G97/G44/G32/G55/G97
/G40/G120/G105/G41 /G78/G111/G40/G120/G105/G105/G41 /G89/G101/G115/G46/G32/G100/G32/G61/G322; /G3250 , 72 , 98
/G40/G120/G105/G105/G105/G41 /G78/G111/G40/G120/G105/G118/G41 /G78/G111/G40/G120/G118/G41 /G89/G101/G115/G46/G32/G100/G32/G61/G32/G50/G52/G59/G32/G57/G55/G44/G32/G49/G50/G49/G44/G32/G49/G52/G53
/G69/G88/G69/G82/G67/G73/G83/G69 /G53/G46/G50
/G49/G46/G40/G105/G41/G97/G110/G32/G61/G32/G50/G56 /G40/G105/G105/G41/G100/G32/G61/G32/G50 /G40/G105/G105/G105/G41/G97/G32/G61/G32/G52/G54 /G40/G105/G118/G41/G110/G32/G61/G32/G49/G48 /G40/G118/G41/G97/G110/G32/G61/G32/G51/G46/G53
```

### 3. pypdfium2 (Current)
```text
8
		9
	 
 	
  &*,	" 	( 	 	5  D'*,	" 	 22 ,
33
 E4	" 	 33
2
±
  			F	 26  			
 C2		$		    C2		$		
 	
  C2	$	$	$	2	2	2	+ "	*	8;	*	*4.	44(0	"		 /*(	/1	*((0		
	)"4(0	"2
  2	? ,	*"	?$	
2 3V 3 , V, 44
⎛⎞ ⎜⎟ ⎝⎠   C2	$	$	$	2	2	2	+ "	*	8;2
  2	8 	*"		
23 88 8 1 10000 1 10000 1 ,, , 100 100 100
⎛ ⎞⎛ ⎞ ⎛ ⎞ ⎜ ⎟⎜ ⎟ ⎜ ⎟ ++ + ⎝ ⎠⎝ ⎠ ⎝ ⎠ 
  $	$	$	  #	$	#	$	#	$	#	  $	$	#	$	#	
 11 –1, 0, ,
22
−  #	2$	#	2	$	#	2$	#	2
  
		$ 		#	  
		#	$ 		
 14 ,
33
ad ==  
		2$ 		2
    C2	
19 , ; 4, 5
22
d =
 C2			#		#	2$	#2$	#	2  C2			 $	$	
 C2			 2 	3 4 2,3 5 2,3 6 2 +++   
 C2			#	 #	$	#	$	#	  C2	
111 0; , ,
222
d =−−−
5  5 C2			
	
$	
$	

5  5 C2			 2; 50 , 72 , 98
5  5  5 C2				$	$	
 	

  
		  		  
		  		  
		2
```

---

## Sample 16 [CHUNK_ID: chk_0886de72963aec15]
**Document:** STD-10/Std-10_Science_English Medium.pdf | **Page:** 183

### 1. PyMuPDF (fitz)
```text
Science
170
What you have learnt
n
The ability of the eye to focus on both near and distant objects, by adjusting its
focal length, is called the accommodation of the eye.
n
The smallest distance, at which the eye can see objects clearly without strain, is
called the near point of the eye or the least distance of distinct vision.  For a young
adult with normal vision, it is about 25 cm.
n
The common refractive defects of vision include myopia, hypermetropia and
presbyopia. Myopia (short-sightedness – the image of distant objects is focussed
before the retina) is corrected by using a concave lens of suitable power.
Hypermetropia (far-sightedness – the image of nearby objects is focussed beyond
the retina) is corrected by using a convex lens of suitable power. The eye loses its
power of accommodation at old age.
n
The splitting of white light into its component colours is called dispersion.
n
Scattering of light causes the blue colour of sky.
E
X
E
R
C
I
S
E
S
1.
The human eye can focus on objects at different distances by adjusting the focal
length of the eye lens. This is due to
 (a)
presbyopia.
(b)
accommodation.
(c)
near-sightedness.
(d)
far-sightedness.
2.
The human eye forms the image of an object at  its
 (a)
cornea.
(b)  iris.
(c)  pupil.
(d)  retina.
3.
The least distance of distinct vision for a young adult with normal vision is about
 (a)
25 m.
(b)  2.5 cm.
(c)  25 cm.
(d)  2.5 m.
4.
The change in focal length of an eye lens is caused by the action of the
 (a)
pupil.
(b)  retina.
(c) ciliary muscles.
(d)  iris.
5.
A person needs a lens of power –5.5 dioptres for correcting his distant vision. For
correcting his near vision he needs a lens of power +1.5 dioptre. What is the focal
length of the lens required for correcting (i) distant vision, and (ii) near vision?
6.
The far point of a myopic person is 80 cm in front of the eye. What is the nature and
power of the lens required to correct the problem?
7.
Make a diagram to show how hypermetropia is corrected. The near point of a
hypermetropic eye is 1 m. What is the power of the lens required to correct this
defect? Assume that the near point of the normal eye is 25 cm.
8.
Why is a normal eye not able to see clearly the objects placed closer than 25 cm?
9.
What happens to the image distance in the eye when we increase the distance of an
object from the eye?
10. Why do stars twinkle?
11. Explain why the planets do not twinkle.
12. Why does the sky appear dark instead of blue to an astronaut?
```

### 2. pypdf (Native)
```text
Science170
What you have learnt
/square6The ability of the eye to focus on both near and distant objects, by adjusting its
focal length, is called the accommodation of the eye.
/square6The smallest distance, at which the eye can see objects clearly without strain, is
called the near point of the eye or the least distance of distinct vision.  For a young
adult with normal vision, it is about 25 cm.
/square6The common refractive defects of vision include myopia, hypermetropia and
presbyopia. Myopia (short-sightedness – the image of distant objects is focussed
before the r etina) is corr ected by using a concave lens of suitable power .
Hypermetropia (far-sightedness – the image of nearby objects is focussed beyond
the retina) is corrected by using a convex lens of suitable power. The eye loses its
power of accommodation at old age.
/square6The splitting of white light into its component colours is called dispersion.
/square6Scattering of light causes the blue colour of sky.
EXERCISES
1. The human eye can focus on objects at different distances by adjusting the focal
length of the eye lens. This is due to
 (a) presbyopia. (b) accommodation.
(c) near-sightedness. (d) far-sightedness.
2. The human eye forms the image of an object at  its
 (a) cornea. (b)  iris. (c)  pupil. (d)  retina.
3. The least distance of distinct vision for a young adult with normal vision is about
 (a) 25 m. (b)  2.5 cm. (c)  25 cm. (d)  2.5 m.
4. The change in focal length of an eye lens is caused by the action of the
 (a) pupil. (b)  retina. (c) ciliary muscles. (d)  iris.
5. A person needs a lens of power –5.5 dioptres for correcting his distant vision. For
correcting his near vision he needs a lens of power +1.5 dioptre. What is the focal
length of the lens required for correcting (i) distant vision, and (ii) near vision?
6. The far point of a myopic person is 80 cm in front of the eye. What is the nature and
power of the lens required to correct the problem?
7. Make a diagram to show how hypermetropia is corrected. The near point of a
hypermetropic eye is 1 m. What is the power of the lens required to correct this
defect? Assume that the near point of the normal eye is 25 cm.
8. Why is a normal eye not able to see clearly the objects placed closer than 25 cm?
9. What happens to the image distance in the eye when we increase the distance of an
object from the eye?
10. Why do stars twinkle?
11. Explain why the planets do not twinkle.
12. Why does the sky appear dark instead of blue to an astronaut?
```

### 3. pypdfium2 (Current)
```text
170 Science
What you have learnt
n The ability of the eye to focus on both near and distant objects, by adjusting its
focal length, is called the accommodation of the eye.
n The smallest distance, at which the eye can see objects clearly without strain, is
called the near point of the eye or the least distance of distinct vision. For a young
adult with normal vision, it is about 25 cm.
n The common refractive defects of vision include myopia, hypermetropia and
presbyopia. Myopia (short-sightedness – the image of distant objects is focussed
before the retina) is corrected by using a concave lens of suitable power.
Hypermetropia (far-sightedness – the image of nearby objects is focussed beyond
the retina) is corrected by using a convex lens of suitable power. The eye loses its
power of accommodation at old age.
n The splitting of white light into its component colours is called dispersion.
n Scattering of light causes the blue colour of sky.
EXERCISES
1. The human eye can focus on objects at different distances by adjusting the focal
length of the eye lens. This is due to
 (a) presbyopia. (b) accommodation.
(c) near-sightedness. (d) far-sightedness.
2. The human eye forms the image of an object at its
 (a) cornea. (b) iris. (c) pupil. (d) retina.
3. The least distance of distinct vision for a young adult with normal vision is about
 (a) 25 m. (b) 2.5 cm. (c) 25 cm. (d) 2.5 m.
4. The change in focal length of an eye lens is caused by the action of the
 (a) pupil. (b) retina. (c) ciliary muscles. (d) iris.
5. A person needs a lens of power –5.5 dioptres for correcting his distant vision. For
correcting his near vision he needs a lens of power +1.5 dioptre. What is the focal
length of the lens required for correcting (i) distant vision, and (ii) near vision?
6. The far point of a myopic person is 80 cm in front of the eye. What is the nature and
power of the lens required to correct the problem?
7. Make a diagram to show how hypermetropia is corrected. The near point of a
hypermetropic eye is 1 m. What is the power of the lens required to correct this
defect? Assume that the near point of the normal eye is 25 cm.
8. Why is a normal eye not able to see clearly the objects placed closer than 25 cm?
9. What happens to the image distance in the eye when we increase the distance of an
object from the eye?
10. Why do stars twinkle?
11. Explain why the planets do not twinkle.
12. Why does the sky appear dark instead of blue to an astronaut?
```

---

## Sample 17 [CHUNK_ID: chk_9c8fc8131ca3eeaf]
**Document:** STD-10/Std-10_Maths_EnglishMedium.pdf | **Page:** 28

### 1. PyMuPDF (fitz)
```text


	



&$
&%
4
%
$
'
"
(
7&'&"
*
4
&"
&*
&*
&"
4
*



,,
 $$
 
   1
#
#
≠4

   
17#
#
     
 ,
  
,

D4E4/
	 
?/$%
&%">
1  -
 $$&%"
B
7&'&"
 B!/

>1
&'&"B
     
 7  & ' & "  
B!
/1

>1
#
#
≠4
B
7#
#B!
 7#
#

;

```

### 2. pypdf (Native)
```text
/G80/G79/G76 /G89/G78/G79/G77/G73/G65/G76/G83 /G49/G51
/G84/G97/G98/G108/G101/G32/G50/G46/G49
/G120 /G150/G32 /G50 /G150 /G49/G48/G49/G50 /G51 /G52 /G53
/G121/G32/G61/G32/G120/G50/G32/G150/G32/G51/G120/G32/G150/G32/G52 /G54 /G48 /G150/G32/G52 /G150/G32/G54 /G150/G32/G54 /G150/G32/G52 /G48 /G54
/G73/G102/G32/G119/G101/G32/G108/G111/G99/G97/G116/G101/G32/G116/G104/G101/G32/G112/G111/G105/G110/G116/G115/G32/G108/G105/G115/G116/G101/G100
/G97/G98/G111/G118/G101/G32/G111/G110/G32/G97/G32/G103/G114/G97/G112/G104/G32/G112/G97/G112/G101/G114/G32/G97/G110/G100/G32/G100/G114/G97/G119
/G116/G104/G101/G32/G103/G114/G97/G112/G104/G44/G32/G105/G116/G32/G119/G105/G108/G108/G32/G97/G99/G116/G117/G97/G108/G108/G121/G32/G108/G111/G111/G107/G32/G108/G105/G107/G101
/G116/G104/G101/G32/G111/G110/G101/G32/G103/G105/G118/G101/G110/G32/G105/G110/G32/G70/G105/G103/G46/G32/G50/G46/G50/G46
/G73/G110/G32/G102/G97/G99/G116/G44/G32/G102/G111/G114/G32/G97/G110/G121/G32/G113/G117/G97/G100/G114/G97/G116/G105/G99
/G112/G111/G108/G121/G110/G111/G109/G105/G97/G108/G32/G97/G120/G50/G32/G43/G32/G98/G120/G32/G43/G32/G99/G44/G32/G97/G32≠/G32/G48/G44/G32/G116/G104/G101
/G103/G114/G97/G112/G104/G32 /G111/G102/G32 /G116/G104/G101/G32 /G99/G111/G114/G114/G101/G115/G112/G111/G110/G100/G105/G110/G103
/G101/G113/G117/G97/G116/G105/G111/G110/G32/G121/G32/G61/G32/G97/G120/G50/G32/G43/G32/G98/G120/G32/G43/G32/G99/G32/G104/G97/G115/G32/G111/G110/G101
/G111/G102/G32/G116/G104/G101/G32/G116/G119/G111/G32/G115/G104/G97/G112/G101/G115/G32/G101/G105/G116/G104/G101/G114/G32/G111/G112/G101/G110
/G117/G112/G119/G97/G114/G100/G115/G32 /G108/G105/G107/G101/G32/G32 /G111/G114/G32 /G111/G112/G101/G110
/G100/G111/G119/G110/G119/G97/G114/G100/G115/G32/G108/G105/G107/G101/G32/G32/G100/G101/G112/G101/G110/G100/G105/G110/G103/G32/G111/G110
/G119/G104/G101/G116/G104/G101/G114/G32/G97/G32/G62/G32/G48/G32/G111/G114/G32/G97/G32/G60/G32/G48/G46/G32/G40/G84/G104/G101/G115/G101
/G99/G117/G114/G118/G101/G115/G32/G97/G114/G101/G32/G99/G97/G108/G108/G101/G100/G32/G112/G97/G114/G97/G98/G111/G108/G97/G115/G46/G41
/G89/G111/G117/G32/G99/G97/G110/G32/G115/G101/G101/G32/G102/G114/G111/G109/G32/G84/G97/G98/G108/G101/G32/G50/G46/G49
/G116/G104/G97/G116/G32/G150/G49/G32/G97/G110/G100/G32/G52/G32/G97/G114/G101/G32/G122/G101/G114/G111/G101/G115/G32/G111/G102/G32/G116/G104/G101
/G113/G117/G97/G100/G114/G97/G116/G105/G99/G32 /G112/G111/G108/G121/G110/G111/G109/G105/G97/G108/G46/G32 /G65/G108/G115/G111
/G110/G111/G116/G101/G32/G102/G114/G111/G109/G32/G70/G105/G103/G46/G32/G50/G46/G50/G32/G116/G104/G97/G116/G32/G150/G49/G32/G97/G110/G100/G32/G52
/G97/G114/G101/G32/G116/G104/G101/G32/G120/G45/G99/G111/G111/G114/G100/G105/G110/G97/G116/G101/G115/G32/G111/G102/G32/G116/G104/G101/G32/G112/G111/G105/G110/G116/G115
/G119/G104/G101/G114/G101/G32/G116/G104/G101/G32/G103/G114/G97/G112/G104/G32/G111/G102/G32/G121/G32/G61/G32/G120/G50/G32/G150/G32/G51/G120/G32/G150/G32/G52
/G105/G110/G116/G101/G114/G115/G101/G99/G116/G115/G32/G116/G104/G101/G32/G120/G45/G97/G120/G105/G115/G46/G32/G84/G104/G117/G115/G44/G32/G116/G104/G101
/G122/G101/G114/G111/G101/G115/G32/G111/G102/G32/G116/G104/G101/G32/G113/G117/G97/G100/G114/G97/G116/G105/G99/G32/G112/G111/G108/G121/G110/G111/G109/G105/G97/G108
/G120/G50/G32/G150/G32/G51/G120/G32/G150/G32/G52/G32/G97/G114/G101/G32/G120/G45/G99/G111/G111/G114/G100/G105/G110/G97/G116/G101/G115/G32/G111/G102
/G116/G104/G101/G32/G112/G111/G105/G110/G116/G115/G32/G119/G104/G101/G114/G101/G32/G116/G104/G101/G32/G103/G114/G97/G112/G104/G32/G111/G102
/G121/G32/G61/G32/G120/G50/G32/G150/G32/G51/G120/G32/G150/G32/G52/G32/G105/G110/G116/G101/G114/G115/G101/G99/G116/G115/G32/G116/G104/G101
/G120/G45/G97/G120/G105/G115/G46
/G84/G104/G105/G115/G32/G102/G97/G99/G116/G32/G105/G115/G32/G116/G114/G117/G101/G32/G102/G111/G114/G32/G97/G110/G121/G32/G113/G117/G97/G100/G114/G97/G116/G105/G99/G32/G112/G111/G108/G121/G110/G111/G109/G105/G97/G108/G44/G32/G105/G46/G101/G46/G44/G32/G116/G104/G101/G32/G122/G101/G114/G111/G101/G115/G32/G111/G102/G32/G97/G32/G113/G117/G97/G100/G114/G97/G116/G105/G99
/G112/G111/G108/G121/G110/G111/G109/G105/G97/G108/G32/G97/G120/G50/G32/G43/G32/G98/G120/G32/G43/G32/G99/G44/G32/G97/G32≠/G32/G48/G44/G32/G97/G114/G101/G32/G112/G114/G101/G99/G105/G115/G101/G108/G121/G32/G116/G104/G101/G32/G120/G45/G99/G111/G111/G114/G100/G105/G110/G97/G116/G101/G115/G32/G111/G102/G32/G116/G104/G101/G32/G112/G111/G105/G110/G116/G115/G32/G119/G104/G101/G114/G101/G32/G116/G104/G101
/G112/G97/G114/G97/G98/G111/G108/G97/G32/G114/G101/G112/G114/G101/G115/G101/G110/G116/G105/G110/G103/G32/G32/G121/G32/G61/G32/G97/G120/G50/G32/G43/G32/G98/G120/G32/G43/G32/G99/G32/G105/G110/G116/G101/G114/G115/G101/G99/G116/G115/G32/G116/G104/G101/G32/G120/G45/G97/G120/G105/G115/G46
/G70/G114/G111/G109/G32/G111/G117/G114/G32/G111/G98/G115/G101/G114/G118/G97/G116/G105/G111/G110/G32/G101/G97/G114/G108/G105/G101/G114/G32/G97/G98/G111/G117/G116/G32/G116/G104/G101/G32/G115/G104/G97/G112/G101/G32/G111/G102/G32/G116/G104/G101/G32/G103/G114/G97/G112/G104/G32/G111/G102/G32/G121/G32/G61/G32/G97/G120/G50/G32/G43/G32/G98/G120/G32/G43/G32/G99/G44/G32/G116/G104/G101
/G102/G111/G108/G108/G111/G119/G105/G110/G103/G32/G116/G104/G114/G101/G101/G32/G99/G97/G115/G101/G115/G32/G99/G97/G110/G32/G104/G97/G112/G112/G101/G110/G58
/G70/G105/G103/G46/G32/G50/G46/G50
```

### 3. pypdfium2 (Current)
```text


	 
 
 & $ &% 4 % $ ' " (
7
&'&" * 4 &" &* &* &" 4 *



,,
 $$
 
   1

#
#
 ≠4

   
17
#
#
   
 ,   
, 
  D 4   E 4 /
	 
?/$%
 &%  "  > 
1  -
   $$ &% "
B
7
&'&"
 B! /

>1

 & ' & "  B 
    
 7 
 & ' & "
B!
/  1

>1

#
#
 ≠4
B
7
#
#B!
 7
#
#

;

```

---

## Sample 18 [CHUNK_ID: chk_80a2ddce53bdd3f7]
**Document:** STD-10/Std-10_Science_English Medium.pdf | **Page:** 219

### 1. PyMuPDF (fitz)
```text
Science
206
What you have learnt
n
A compass needle is a small magnet. Its one end, which points towards north, is
called a north pole, and the other end, which points towards south, is called a
south pole.
n
A magnetic field exists in the region surrounding a magnet, in which the force of
the magnet can be detected.
n
Field lines are used to represent a magnetic field. A field line is the path along
which a hypothetical free north pole would tend to move. The direction of the
magnetic field at a point is given by the direction that a north pole placed at that
point would take. Field lines are shown closer together where the magnetic field is
greater.
n
A metallic wire carrying an electric current has associated with it a magnetic field.
The field lines about the wire consist of a series of concentric circles whose direction
is given by the right-hand rule.
n
The pattern of the magnetic field around a conductor due to an electric current
flowing through it depends on the shape of the conductor. The magnetic field of a
solenoid carrying a current is similar to that of a bar magnet.
n
An electromagnet consists of a core of soft iron wrapped around with a coil of
insulated copper wire.
n
A current-carrying conductor when placed in a magnetic field experiences a force.
If the direction of the field and that of the current are mutually perpendicular to
each other, then the force acting on the conductor will be perpendicular to both
and will be given by Fleming’s left-hand rule.
n
In our houses we receive AC electric power of 220 V with a frequency of 50 Hz. One
of the wires in this supply is with red insulation, called live wire. The other one is of
black insulation, which is a neutral wire. The potential difference between the two
is 220 V. The third is the earth wire that has green insulation and this is connected
to a metallic body deep inside earth. It is used as a safety measure to ensure that
any leakage of current to a metallic body does not give any severe shock to a user.
n
Fuse is the most important safety device, used for protecting the circuits due to
short-circuiting or overloading of the circuits.
```

### 2. pypdf (Native)
```text
Science206
What you have learnt
/square6A compass needle is a small magnet. Its one end, which points towards north, is
called a north pole, and the other end, which points towards south, is called a
south pole.
/square6A magnetic field exists in the region surrounding a magnet, in which the force of
the magnet can be detected.
/square6Field lines are used to represent a magnetic field. A field line is the path along
which a hypothetical free north pole would tend to move. The direction of the
magnetic field at a point is given by the direction that a north pole placed at that
point would take. Field lines are shown closer together where the magnetic field is
greater.
/square6A metallic wire carrying an electric current has associated with it a magnetic field.
The field lines about the wire consist of a series of concentric circles whose direction
is given by the right-hand rule.
/square6The pattern of the magnetic field around a conductor due to an electric current
flowing through it depends on the shape of the conductor. The magnetic field of a
solenoid carrying a current is similar to that of a bar magnet.
/square6An electromagnet consists of a core of soft iron wrapped around with a coil of
insulated copper wire.
/square6A current-carrying conductor when placed in a magnetic field experiences a force.
If the direction of the field and that of the current are mutually perpendicular to
each other, then the force acting on the conductor will be perpendicular to both
and will be given by Fleming’s left-hand rule.
/square6In our houses we receive AC electric power of 220 V with a frequency of 50 Hz. One
of the wires in this supply is with red insulation, called live wire. The other one is of
black insulation, which is a neutral wire. The potential difference between the two
is 220 V. The third is the earth wire that has green insulation and this is connected
to a metallic body deep inside earth. It is used as a safety measure to ensure that
any leakage of current to a metallic body does not give any severe shock to a user.
/square6Fuse is the most important safety device, used for protecting the circuits due to
short-circuiting or overloading of the circuits.
```

### 3. pypdfium2 (Current)
```text
206 Science
What you have learnt
n A compass needle is a small magnet. Its one end, which points towards north, is
called a north pole, and the other end, which points towards south, is called a
south pole.
n A magnetic field exists in the region surrounding a magnet, in which the force of
the magnet can be detected.
n Field lines are used to represent a magnetic field. A field line is the path along
which a hypothetical free north pole would tend to move. The direction of the
magnetic field at a point is given by the direction that a north pole placed at that
point would take. Field lines are shown closer together where the magnetic field is
greater.
n A metallic wire carrying an electric current has associated with it a magnetic field.
The field lines about the wire consist of a series of concentric circles whose direction
is given by the right-hand rule.
n The pattern of the magnetic field around a conductor due to an electric current
flowing through it depends on the shape of the conductor. The magnetic field of a
solenoid carrying a current is similar to that of a bar magnet.
n An electromagnet consists of a core of soft iron wrapped around with a coil of
insulated copper wire.
n A current-carrying conductor when placed in a magnetic field experiences a force.
If the direction of the field and that of the current are mutually perpendicular to
each other, then the force acting on the conductor will be perpendicular to both
and will be given by Fleming’s left-hand rule.
n In our houses we receive AC electric power of 220 V with a frequency of 50 Hz. One
of the wires in this supply is with red insulation, called live wire. The other one is of
black insulation, which is a neutral wire. The potential difference between the two
is 220 V. The third is the earth wire that has green insulation and this is connected
to a metallic body deep inside earth. It is used as a safety measure to ensure that
any leakage of current to a metallic body does not give any severe shock to a user.
n Fuse is the most important safety device, used for protecting the circuits due to
short-circuiting or overloading of the circuits.
```

---

## Sample 19 [CHUNK_ID: chk_c264215316396e8a]
**Document:** STD-10/Std-10_Maths_EnglishMedium.pdf | **Page:** 240

### 1. PyMuPDF (fitz)
```text

		
)
:!853!PQP&




	!P
#

PQDP&/56=0
#!

	!	

	





	


	
!

L!


)

(



/		 	!0		!
	




	/!0	


	





8	!




PQDP&



!


!


 		!	
	
	


	




!



 
C		





!	


1 	



			
/	
0
	
			
	
-
!
	
	
	
(*(

)	./
5
-
	

	
" 
 	
  

	!

!
	

!
	
=
-

m
x
n
=
≠6
p
y
q
=
≠6
!

3
"
m
p
mq
np
x
y
n
q
nq
+
+
=
+
=
'	!()(
8	



	
	

	



	!	

	K

```

### 2. pypdf (Native)
```text
/G80/G82/G79/G79/G70/G83/G32/G73/G78/G32/G77/G65 /G84/G72/G69/G77/G65 /G84/G73/G67/G83 /G50/G50/G53
/G78/G111/G119/G44/G32/G99/G111/G110/G115/G105/G100/G101/G114/G32/G70/G105/G103/G46/G32/G65/G49/G46/G51/G44/G32/G119/G104/G101/G114/G101/G32/G80/G81/G32/G97/G110/G100/G32/G80/G82
/G97/G114/G101/G32/G116/G97/G110/G103/G101/G110/G116/G115/G32/G116/G111/G32/G116/G104/G101/G32/G99/G105/G114/G99/G108/G101/G32/G100/G114/G97/G119/G110/G32/G32/G102/G114/G111/G109/G32/G80/G46
/G89/G111/G117/G32/G104/G97/G118/G101/G32/G112/G114/G111/G118/G101/G100/G32/G116/G104/G97/G116/G32/G80/G81/G32/G61/G32/G80/G82/G32/G40/G84/G104/G101/G111/G114/G101/G109/G32/G49/G48/G46/G50/G41/G46
/G89/G111/G117/G32/G119/G101/G114/G101/G32/G110/G111/G116/G32/G115/G97/G116/G105/G115/G102/G105/G101/G100/G32/G98/G121/G32/G111/G110/G108/G121/G32/G100/G114/G97/G119/G105/G110/G103/G32/G115/G101/G118/G101/G114/G97/G108/G32/G115/G117/G99/G104
/G102/G105/G103/G117/G114/G101/G115/G44/G32/G109/G101/G97/G115/G117/G114/G105/G110/G103/G32/G116/G104/G101/G32/G108/G101/G110/G103/G116/G104/G115/G32/G111/G102/G32/G116/G104/G101/G32/G114/G101/G115/G112/G101/G99/G116/G105/G118/G101
/G116/G97/G110/G103/G101/G110/G116/G115/G44/G32/G97/G110/G100/G32/G118/G101/G114/G105/G102/G121/G105/G110/G103/G32/G102/G111/G114/G32/G121/G111/G117/G114/G115/G101/G108/G118/G101/G115/G32/G116/G104/G97/G116/G32/G116/G104/G101/G32/G114/G101/G115/G117/G108/G116
/G119/G97/G115/G32/G116/G114/G117/G101/G32/G105/G110/G32/G101/G97/G99/G104/G32/G99/G97/G115/G101/G46
/G68/G111/G32/G121/G111/G117/G32/G114/G101/G109/G101/G109/G98/G101/G114/G32/G119/G104/G97/G116/G32/G100/G105/G100/G32/G116/G104/G101/G32/G112/G114/G111/G111/G102/G32/G99/G111/G110/G115/G105/G115/G116/G32/G111/G102/G32/G63/G32/G73/G116/G32/G99/G111/G110/G115/G105/G115/G116/G101/G100/G32/G111/G102/G32/G97/G32/G115/G101/G113/G117/G101/G110/G99/G101/G32/G111/G102
/G115/G116/G97/G116/G101/G109/G101/G110/G116/G115/G32/G40/G99/G97/G108/G108/G101/G100/G32/G118/G97/G108/G105/G100/G32/G97/G114/G103/G117/G109/G101/G110/G116/G115/G41/G44/G32/G101/G97/G99/G104/G32/G102/G111/G108/G108/G111/G119/G105/G110/G103/G32/G102/G114/G111/G109/G32/G116/G104/G101/G32/G101/G97/G114/G108/G105/G101/G114/G32/G115/G116/G97/G116/G101/G109/G101/G110/G116/G115/G32/G105/G110
/G116/G104/G101/G32/G112/G114/G111/G111/G102/G44/G32/G111/G114/G32/G102/G114/G111/G109/G32/G112/G114/G101/G118/G105/G111/G117/G115/G108/G121/G32/G112/G114/G111/G118/G101/G100/G32/G40/G97/G110/G100/G32/G107/G110/G111/G119/G110/G41/G32/G114/G101/G115/G117/G108/G116/G115/G32/G105/G110/G100/G101/G112/G101/G110/G100/G101/G110/G116/G32/G102/G114/G111/G109/G32/G116/G104/G101/G32/G114/G101/G115/G117/G108/G116
/G116/G111/G32/G98/G101/G32/G112/G114/G111/G118/G101/G100/G44/G32/G111/G114/G32/G102/G114/G111/G109/G32/G97/G120/G105/G111/G109/G115/G44/G32/G111/G114/G32/G102/G114/G111/G109/G32/G100/G101/G102/G105/G110/G105/G116/G105/G111/G110/G115/G44/G32/G111/G114/G32/G102/G114/G111/G109/G32/G116/G104/G101/G32/G97/G115/G115/G117/G109/G112/G116/G105/G111/G110/G115/G32/G121/G111/G117/G32/G104/G97/G100
/G109/G97/G100/G101/G46/G32/G65/G110/G100/G32/G121/G111/G117/G32/G99/G111/G110/G99/G108/G117/G100/G101/G100/G32/G121/G111/G117/G114/G32/G112/G114/G111/G111/G102/G32/G119/G105/G116/G104/G32/G116/G104/G101/G32/G115/G116/G97/G116/G101/G109/G101/G110/G116/G32/G80/G81/G32/G61/G32/G80/G82/G44/G32/G105/G46/G101/G46/G44/G32/G116/G104/G101/G32/G115/G116/G97/G116/G101/G109/G101/G110/G116
/G121/G111/G117/G32/G119/G97/G110/G116/G101/G100/G32/G116/G111/G32/G112/G114/G111/G118/G101/G46/G32/G84/G104/G105/G115/G32/G105/G115/G32/G116/G104/G101/G32/G119/G97/G121/G32/G97/G110/G121/G32/G112/G114/G111/G111/G102/G32/G105/G115/G32/G99/G111/G110/G115/G116/G114/G117/G99/G116/G101/G100/G46
/G87/G101/G32/G115/G104/G97/G108/G108/G32/G110/G111/G119/G32/G108/G111/G111/G107/G32/G97/G116/G32/G115/G111/G109/G101/G32/G101/G120/G97/G109/G112/G108/G101/G115/G32/G97/G110/G100/G32/G116/G104/G101/G111/G114/G101/G109/G115/G32/G97/G110/G100/G32/G97/G110/G97/G108/G121/G115/G101/G32/G116/G104/G101/G105/G114/G32/G112/G114/G111/G111/G102/G115/G32/G116/G111
/G104/G101/G108/G112/G32/G117/G115/G32/G105/G110/G32/G103/G101/G116/G116/G105/G110/G103/G32/G97/G32/G98/G101/G116/G116/G101/G114/G32/G117/G110/G100/G101/G114/G115/G116/G97/G110/G100/G105/G110/G103/G32/G111/G102/G32/G104/G111/G119/G32/G116/G104/G101/G121/G32/G97/G114/G101/G32/G99/G111/G110/G115/G116/G114/G117/G99/G116/G101/G100/G46
/G87/G101/G32/G98/G101/G103/G105/G110/G32/G98/G121/G32/G117/G115/G105/G110/G103/G32/G116/G104/G101/G32/G115/G111/G45/G99/G97/G108/G108/G101/G100/G32/G145/G100/G105/G114/G101/G99/G116/G146/G32/G111/G114/G32/G145/G100/G101/G100/G117/G99/G116/G105/G118/G101/G146/G32/G109/G101/G116/G104/G111/G100/G32/G111/G102/G32/G112/G114/G111/G111/G102/G46/G32/G73/G110/G32/G116/G104/G105/G115
/G109/G101/G116/G104/G111/G100/G44/G32/G119/G101/G32/G109/G97/G107/G101/G32/G115/G101/G118/G101/G114/G97/G108/G32/G115/G116/G97/G116/G101/G109/G101/G110/G116/G115/G46/G32/G69/G97/G99/G104/G32/G105/G115/G32/G98/G97/G115/G101/G100/G32/G111/G110/G32/G112/G114/G101/G118/G105/G111/G117/G115/G32/G115/G116/G97/G116/G101/G109/G101/G110/G116/G115/G46/G32/G73/G102
/G101/G97/G99/G104/G32/G115/G116/G97/G116/G101/G109/G101/G110/G116/G32/G105/G115/G32/G108/G111/G103/G105/G99/G97/G108/G108/G121/G32/G99/G111/G114/G114/G101/G99/G116/G32/G40/G105/G46/G101/G46/G44/G32/G97/G32/G118/G97/G108/G105/G100/G32/G97/G114/G103/G117/G109/G101/G110/G116/G41/G44/G32/G105/G116/G32/G108/G101/G97/G100/G115/G32/G116/G111/G32/G97/G32/G108/G111/G103/G105/G99/G97/G108/G108/G121/G32/G99/G111/G114/G114/G101/G99/G116
/G99/G111/G110/G99/G108/G117/G115/G105/G111/G110/G46
/G69/G120/G97/G109/G112/G108/G101/G32/G49/G48/G32/G58/G32/G84/G104/G101/G32/G115/G117/G109/G32/G111/G102/G32/G116/G119/G111/G32/G114/G97/G116/G105/G111/G110/G97/G108/G32/G110/G117/G109/G98/G101/G114/G115/G32/G105/G115/G32/G97/G32/G114/G97/G116/G105/G111/G110/G97/G108/G32/G110/G117/G109/G98/G101/G114/G46
/G83/G111/G108/G117/G116/G105/G111/G110/G32/G58
/G83/G46/G78/G111/G46/G83/G116/G97/G116/G101/G109/G101/G110/G116/G115/G65/G110/G97/G108/G121/G115/G105/G115/G47/G67/G111/G109/G109/G101/G110/G116/G115
/G49/G46/G76/G101/G116/G32/G120
/G32/G97/G110/G100/G32/G121/G32/G98/G101/G32/G114/G97/G116/G105/G111/G110/G97/G108/G32/G110/G117/G109/G98/G101/G114/G115/G46 /G83/G105/G110/G99/G101/G32/G116/G104/G101/G32/G114/G101/G115/G117/G108/G116/G32/G105/G115/G32/G97/G98/G111/G117/G116
/G114/G97/G116/G105/G111/G110/G97/G108/G115/G44/G32/G119/G101/G32/G115/G116/G97/G114/G116/G32/G119/G105/G116/G104/G32/G120/G32/G97/G110/G100
/G121/G32/G119/G104/G105/G99/G104/G32/G97/G114/G101/G32/G114/G97/G116/G105/G111/G110/G97/G108/G46
/G50/G46 /G76/G101/G116/G32mx n= /G44/G32/G110/G32≠/G32/G48/G32/G97/G110/G100/G32py q= /G44/G32/G113/G32≠/G32/G48
/G119/G104/G101/G114/G101/G32/G109/G44/G32/G110/G44/G32/G112/G32/G97/G110/G100/G32/G113/G32/G97/G114/G101/G32/G105/G110/G116/G101/G103/G101/G114/G115/G46
/G51/G46 /G83/G111/G44/G32mpm q n pxy nq n q
++= + =
/G70/G105/G103/G46/G32/G65/G49/G46/G51
/G65/G112/G112/G108/G121/G32/G116/G104/G101/G32/G100/G101/G102/G105/G110/G105/G116/G105/G111/G110/G32/G111/G102
/G114/G97/G116/G105/G111/G110/G97/G108/G115/G46
/G84/G104/G101/G32/G114/G101/G115/G117/G108/G116/G32
/G116/G97/G108/G107/G115/G32/G97/G98/G111/G117/G116/G32/G116/G104/G101
/G115/G117/G109/G32/G111/G102/G32/G114/G97/G116/G105/G111/G110/G97/G108/G115/G44/G32/G115/G111/G32/G119/G101/G32/G108/G111/G111/G107
/G97/G116/G32/G120/G32/G43/G32/G121/G46
```

### 3. pypdfium2 (Current)
```text

	 	 )
:!  853 ! PQ  P&




	!P
#

PQDP&/56=0
#!

	!	

	
 
 



	


	

!

L!


)

(



/		 	!0		!
	




	/!0	


	






8	!




PQDP&




!


!


 		!	
	
	


	




!



 
C		





 ! 	 


 1   	  



			
/	
0
	
			

	
-
!
	
	
	
(*(  )	./
5 -
	

	 " 
	
 


	!

!
	

!
	
= -
 m
x
n =  ≠6 p y
q =  ≠6
!

3 " m p mq np xy
n q nq
+
+= + =
'	!()(
8	



	
	

	



	!	

	K

```

---

## Sample 20 [CHUNK_ID: chk_aac1f2441f48427f]
**Document:** STD-10/Std-10_Science_English Medium.pdf | **Page:** 126

### 1. PyMuPDF (fitz)
```text
How do Organisms
Reproduce?
7
CHAPTER
B
efore we discuss the mechanisms by which organisms reproduce,
let us ask a more basic question – why do organisms reproduce?
After all, reproduction is not necessary to maintain the life of an individual
organism, unlike the essential life processes such as nutrition,
respiration, or excretion. On the other hand, if an individual organism is
going to create more individuals, a lot of its energy will be spent in the
process. So why should an individual organism waste energy on a process
it does not need to stay alive? It would be interesting to discuss the
possible answers in the classroom!
Whatever the answer to this question, it is obvious that we notice
organisms because they reproduce. If there were to be only one, non-
reproducing member of a particular kind, it is doubtful that we would
have noticed its existence. It is the large numbers of organisms belonging
to a single species that bring them to our notice. How do we know that
two different individual organisms belong to the same species? Usually,
we say this because they look similar to each other. Thus, reproducing
organisms create new individuals that look very much like themselves.
7.1 DO ORG
7.1 DO ORG
7.1 DO ORG
7.1 DO ORG
7.1 DO ORGANISMS CREA
ANISMS CREA
ANISMS CREA
ANISMS CREA
ANISMS CREATE EXA
TE EXA
TE EXA
TE EXA
TE EXACT COPIES OF
CT COPIES OF
CT COPIES OF
CT COPIES OF
CT COPIES OF
THEMSEL
THEMSEL
THEMSEL
THEMSEL
THEMSELVES?
VES?
VES?
VES?
VES?
Organisms look similar because their body designs are similar. If body
designs are to be similar, the blueprints for these designs should be
similar. Thus, reproduction at its most basic level will involve making
copies of the blueprints of body design. In Class IX, we learnt that the
chromosomes in the nucleus of a cell contain information for inheritance
of features from parents to next generation in the form of DNA (Deoxyribo
Nucleic Acid) molecules. The DNA in the cell nucleus is the information
source for making proteins. If the information is changed, different
proteins will be made. Different proteins will eventually lead to altered
body designs.
Therefore, a basic event in reproduction is the creation of a DNA
copy. Cells use chemical reactions to build copies of their DNA. This
creates two copies of the DNA in a reproducing cell, and they will need to
be separated from each other. However, keeping one copy of DNA in the
original cell and simply pushing the other one out would not work,
```

### 2. pypdf (Native)
```text
How do Organisms
Reproduce?
7CHAPTER
B
efore we discuss the mechanisms by which organisms reproduce,
let us ask a more basic question – why do organisms reproduce?
After all, reproduction is not necessary to maintain the life of an individual
organism, unlike the essential life processes such as nutrition,
respiration, or excretion. On the other hand, if an individual organism is
going to create more individuals, a lot of its energy will be spent in the
process. So why should an individual organism waste energy on a process
it does not need to stay alive? It would be interesting to discuss the
possible answers in the classroom!
Whatever the answer to this question, it is obvious that we notice
organisms because they reproduce. If there were to be only one, non-
reproducing member of a particular kind, it is doubtful that we would
have noticed its existence. It is the large numbers of organisms belonging
to a single species that bring them to our notice. How do we know that
two different individual organisms belong to the same species? Usually,
we say this because they look similar to each other. Thus, reproducing
organisms create new individuals that look very much like themselves.
7.1 DO ORG7.1 DO ORG7.1 DO ORG7.1 DO ORG7.1 DO ORG ANISMS CREAANISMS CREAANISMS CREAANISMS CREAANISMS CREA TE EXA TE EXATE EXA TE EXATE EXA CT COPIES OFCT COPIES OFCT COPIES OFCT COPIES OFCT COPIES OF
THEMSEL THEMSELTHEMSEL THEMSELTHEMSEL VES? VES?VES? VES?VES?
Organisms look similar because their body designs are similar. If body
designs are to be similar, the blueprints for these designs should be
similar. Thus, reproduction at its most basic level will involve making
copies of the blueprints of body design. In Class IX, we learnt that the
chromosomes in the nucleus of a cell contain information for inheritance
of features from parents to next generation in the form of DNA (Deoxyribo
Nucleic Acid) molecules. The DNA in the cell nucleus is the information
source for making proteins. If the information is changed, different
proteins will be made. Different proteins will eventually lead to altered
body designs.
Therefore, a basic event in reproduction is the creation of a DNA
copy. Cells use chemical reactions to build copies of their DNA. This
creates two copies of the DNA in a reproducing cell, and they will need to
be separated from each other. However, keeping one copy of DNA in the
original cell and simply pushing the other one out would not work,
```

### 3. pypdfium2 (Current)
```text
How do Organisms
Reproduce?
CHAPTER7
B
efore we discuss the mechanisms by which organisms reproduce,
let us ask a more basic question – why do organisms reproduce?
After all, reproduction is not necessary to maintain the life of an individual
organism, unlike the essential life processes such as nutrition,
respiration, or excretion. On the other hand, if an individual organism is
going to create more individuals, a lot of its energy will be spent in the
process. So why should an individual organism waste energy on a process
it does not need to stay alive? It would be interesting to discuss the
possible answers in the classroom!
Whatever the answer to this question, it is obvious that we notice
organisms because they reproduce. If there were to be only one, nonreproducing member of a particular kind, it is doubtful that we would
have noticed its existence. It is the large numbers of organisms belonging
to a single species that bring them to our notice. How do we know that
two different individual organisms belong to the same species? Usually,
we say this because they look similar to each other. Thus, reproducing
organisms create new individuals that look very much like themselves.
7.1 DO ORGANISMS CREATE EXACT COPIES OF
THEMSEL THEMSELVES?
Organisms look similar because their body designs are similar. If body
designs are to be similar, the blueprints for these designs should be
similar. Thus, reproduction at its most basic level will involve making
copies of the blueprints of body design. In Class IX, we learnt that the
chromosomes in the nucleus of a cell contain information for inheritance
of features from parents to next generation in the form of DNA (Deoxyribo
Nucleic Acid) molecules. The DNA in the cell nucleus is the information
source for making proteins. If the information is changed, different
proteins will be made. Different proteins will eventually lead to altered
body designs.
Therefore, a basic event in reproduction is the creation of a DNA
copy. Cells use chemical reactions to build copies of their DNA. This
creates two copies of the DNA in a reproducing cell, and they will need to
be separated from each other. However, keeping one copy of DNA in the
original cell and simply pushing the other one out would not work,
```

---

## Sample 21 [CHUNK_ID: chk_9515abc17a33523f]
**Document:** STD-10/Std-10_Maths_EnglishMedium.pdf | **Page:** 255

### 1. PyMuPDF (fitz)
```text


12 5	'	
		
		
12 4		'	
	

12 5	'	
			
12 4		'	
	
12 4		'	
				
	
	
12 4		'	
				
	
12 4		'	
			
 /
)	

	$
		
	
	'	
	
$				
) 	66$	
	
'
	
	'') 	67$	
) 	68$		
		
	
'
			
	
$	$		$
$

	
	
	,$#$	$
	
				
$	
	')

'
''	
$
 	
		
)")*$	
'&	
'
'
			
	
		%9	-		

		
	'




	

&	
$'
		
	
	$
		 '	
''			
		
'
3				

)	
			
	

		
(	
					
		
	



	


	

&	
	
		
			
 $		
	
	
	0
 
 $	-	-	
 '	
	'		
 '

 		
```

### 2. pypdf (Native)
```text
/G50/G52/G48 /G77/G65 /G84/G72/G69/G77/G65 /G84/G73/G67/G83
/G40/G118/G41 /G80/G114/G101/G100/G105/G99/G116/G105/G110/G103/G32/G116/G104/G101/G32/G116/G114/G101/G110/G100/G32/G111/G102/G32/G116/G104/G101/G32/G115/G116/G111/G99/G107/G32/G109/G97/G114/G107/G101/G116/G46
/G40/G118/G105/G41/G69/G115/G116/G105/G109/G97/G116/G105/G110/G103/G32/G116/G104/G101/G32/G118/G111/G108/G117/G109/G101/G32/G111/G102/G32/G98/G108/G111/G111/G100/G32/G105/G110/G115/G105/G100/G101/G32/G116/G104/G101/G32/G98/G111/G100/G121/G32/G111/G102/G32/G97/G32/G112/G101/G114/G115/G111/G110/G46
/G40/G118/G105/G105/G41/G80/G114/G101/G100/G105/G99/G116/G105/G110/G103/G32/G116/G104/G101/G32/G112/G111/G112/G117/G108/G97/G116/G105/G111/G110/G32/G111/G102/G32/G97/G32/G99/G105/G116/G121/G32/G97/G102/G116/G101/G114/G32/G49/G48/G32/G121/G101/G97/G114/G115/G46
/G40/G118/G105/G105/G105/G41/G69/G115/G116/G105/G109/G97/G116/G105/G110/G103/G32/G116/G104/G101/G32/G110/G117/G109/G98/G101/G114/G32/G111/G102/G32/G108/G101/G97/G118/G101/G115/G32/G105/G110/G32/G97/G32/G116/G114/G101/G101/G46
/G40/G105/G120/G41 /G69/G115/G116/G105/G109/G97/G116/G105/G110/G103/G32/G116/G104/G101/G32/G112/G112/G109/G32/G111/G102/G32/G100/G105/G102/G102/G101/G114/G101/G110/G116/G32/G112/G111/G108/G108/G117/G116/G97/G110/G116/G115/G32/G105/G110/G32/G116/G104/G101/G32/G97/G116/G109/G111/G115/G112/G104/G101/G114/G101/G32/G111/G102/G32/G97/G32/G99/G105/G116/G121/G46
/G40/G120/G41 /G69/G115/G116/G105/G109/G97/G116/G105/G110/G103/G32/G116/G104/G101/G32/G101/G102/G102/G101/G99/G116/G32/G111/G102/G32/G112/G111/G108/G108/G117/G116/G97/G110/G116/G115/G32/G111/G110/G32/G116/G104/G101/G32/G101/G110/G118/G105/G114/G111/G110/G109/G101/G110/G116/G46
/G40/G120/G105/G41/G69/G115/G116/G105/G109/G97/G116/G105/G110/G103/G32/G116/G104/G101/G32/G116/G101/G109/G112/G101/G114/G97/G116/G117/G114/G101/G32/G111/G110/G32/G116/G104/G101/G32/G83/G117/G110/G146/G115/G32/G115/G117/G114/G102/G97/G99/G101/G46
/G73/G110/G32/G116/G104/G105/G115/G32/G99/G104/G97/G112/G116/G101/G114/G32/G119/G101/G32/G115/G104/G97/G108/G108/G32/G114/G101/G118/G105/G115/G105/G116/G32/G116/G104/G101/G32/G112/G114/G111/G99/G101/G115/G115/G32/G111/G102/G32/G109/G97/G116/G104/G101/G109/G97/G116/G105/G99/G97/G108/G32/G109/G111/G100/G101/G108/G108/G105/G110/G103/G44/G32/G97/G110/G100/G32/G116/G97/G107/G101
/G101/G120/G97/G109/G112/G108/G101/G115/G32/G102/G114/G111/G109/G32/G116/G104/G101/G32/G119/G111/G114/G108/G100/G32/G97/G114/G111/G117/G110/G100/G32/G117/G115/G32/G116/G111/G32/G105/G108/G108/G117/G115/G116/G114/G97/G116/G101/G32/G116/G104/G105/G115/G46/G32/G73/G110/G32/G83/G101/G99/G116/G105/G111/G110/G32/G65/G50/G46/G50/G32/G119/G101/G32/G116/G97/G107/G101/G32/G121/G111/G117
/G116/G104/G114/G111/G117/G103/G104/G32/G97/G108/G108/G32/G116/G104/G101/G32/G115/G116/G97/G103/G101/G115/G32/G111/G102/G32/G98/G117/G105/G108/G100/G105/G110/G103/G32/G97/G32/G109/G111/G100/G101/G108/G46/G32/G73/G110/G32/G83/G101/G99/G116/G105/G111/G110/G32/G65/G50/G46/G51/G44/G32/G119/G101/G32/G100/G105/G115/G99/G117/G115/G115/G32/G97/G32/G118/G97/G114/G105/G101/G116/G121/G32/G111/G102
/G101/G120/G97/G109/G112/G108/G101/G115/G46/G32/G73/G110/G32/G83/G101/G99/G116/G105/G111/G110/G32/G65/G50/G46/G52/G44/G32/G119/G101/G32/G108/G111/G111/G107/G32/G97/G116/G32/G114/G101/G97/G115/G111/G110/G115/G32/G102/G111/G114/G32/G116/G104/G101/G32/G105/G109/G112/G111/G114/G116/G97/G110/G99/G101/G32/G111/G102/G32/G109/G97/G116/G104/G101/G109/G97/G116/G105/G99/G97/G108
/G109/G111/G100/G101/G108/G108/G105/G110/G103/G46
/G65/G32/G112/G111/G105/G110/G116/G32/G116/G111/G32/G114/G101/G109/G101/G109/G98/G101/G114/G32/G105/G115/G32/G116/G104/G97/G116/G32/G104/G101/G114/G101/G32/G119/G101/G32/G97/G105/G109/G32/G116/G111/G32/G109/G97/G107/G101/G32/G121/G111/G117/G32/G97/G119/G97/G114/G101/G32/G111/G102/G32/G97/G110/G32/G105/G109/G112/G111/G114/G116/G97/G110/G116/G32/G119/G97/G121
/G105/G110/G32/G119/G104/G105/G99/G104/G32/G109/G97/G116/G104/G101/G109/G97/G116/G105/G99/G115/G32/G104/G101/G108/G112/G115/G32/G116/G111/G32/G115/G111/G108/G118/G101/G32/G114/G101/G97/G108/G45/G119/G111/G114/G108/G100/G32/G112/G114/G111/G98/G108/G101/G109/G115/G46/G32/G72/G111/G119/G101/G118/G101/G114/G44/G32/G121/G111/G117/G32/G110/G101/G101/G100/G32/G116/G111/G32/G107/G110/G111/G119
/G115/G111/G109/G101/G32/G109/G111/G114/G101/G32/G109/G97/G116/G104/G101/G109/G97/G116/G105/G99/G115/G32/G116/G111/G32/G114/G101/G97/G108/G108/G121/G32/G97/G112/G112/G114/G101/G99/G105/G97/G116/G101/G32/G116/G104/G101/G32/G112/G111/G119/G101/G114/G32/G111/G102/G32/G109/G97/G116/G104/G101/G109/G97/G116/G105/G99/G97/G108/G32/G109/G111/G100/G101/G108/G108/G105/G110/G103/G46/G32/G73/G110
/G104/G105/G103/G104/G101/G114/G32/G99/G108/G97/G115/G115/G101/G115/G32/G115/G111/G109/G101/G32/G101/G120/G97/G109/G112/G108/G101/G115/G32/G103/G105/G118/G105/G110/G103/G32/G116/G104/G105/G115/G32/G102/G108/G97/G118/G111/G117/G114/G32/G119/G105/G108/G108/G32/G98/G101/G32/G102/G111/G117/G110/G100/G46
/G65/G50/G46/G50 /G83/G116/G97/G103/G101/G115/G32/G105/G110/G32/G77/G97/G116/G104/G101/G109/G97/G116/G105/G99/G97/G108/G32/G77/G111/G100/G101/G108/G108/G105/G110/G103
/G73/G110/G32/G67/G108/G97/G115/G115/G32/G73/G88/G44/G32/G119/G101/G32/G99/G111/G110/G115/G105/G100/G101/G114/G101/G100/G32/G115/G111/G109/G101/G32/G101/G120/G97/G109/G112/G108/G101/G115/G32/G111/G102/G32/G116/G104/G101/G32/G117/G115/G101/G32/G111/G102/G32/G109/G111/G100/G101/G108/G108/G105/G110/G103/G46/G32/G68/G105/G100/G32/G116/G104/G101/G121/G32/G103/G105/G118/G101/G32/G121/G111/G117
/G97/G110/G32/G105/G110/G115/G105/G103/G104/G116/G32/G105/G110/G116/G111/G32/G116/G104/G101/G32/G112/G114/G111/G99/G101/G115/G115/G32/G97/G110/G100/G32/G116/G104/G101/G32/G115/G116/G101/G112/G115/G32/G105/G110/G118/G111/G108/G118/G101/G100/G32/G105/G110/G32/G105/G116/G63/G32/G76/G101/G116/G32/G117/G115/G32/G113/G117/G105/G99/G107/G108/G121/G32/G114/G101/G118/G105/G115/G105/G116/G32/G116/G104/G101/G32/G109/G97/G105/G110
/G115/G116/G101/G112/G115/G32/G105/G110/G32/G109/G97/G116/G104/G101/G109/G97/G116/G105/G99/G97/G108/G32/G109/G111/G100/G101/G108/G108/G105/G110/G103/G46
/G83/G116/G101/G112/G32/G49/G32/G40/G85/G110/G100/G101/G114/G115/G116/G97/G110/G100/G105/G110/G103/G32/G116/G104/G101/G32/G112/G114/G111/G98/G108/G101/G109/G41/G32/G58/G32/G68/G101/G102/G105/G110/G101/G32/G116/G104/G101/G32 /G114/G101/G97/G108/G32/G112/G114/G111/G98/G108/G101/G109/G44/G32/G97/G110/G100/G32/G105/G102/G32/G119/G111/G114/G107/G105/G110/G103/G32/G105/G110/G32/G97
/G116/G101/G97/G109/G44/G32/G100/G105/G115/G99/G117/G115/G115/G32/G116/G104/G101/G32/G105/G115/G115/G117/G101/G115/G32/G116/G104/G97/G116/G32/G121/G111/G117/G32/G119/G105/G115/G104/G32/G116/G111/G32/G117/G110/G100/G101/G114/G115/G116/G97/G110/G100/G46/G32/G83/G105/G109/G112/G108/G105/G102/G121/G32/G98/G121/G32/G109/G97/G107/G105/G110/G103/G32/G97/G115/G115/G117/G109/G112/G116/G105/G111/G110/G115
/G97/G110/G100/G32/G105/G103/G110/G111/G114/G105/G110/G103/G32/G99/G101/G114/G116/G97/G105/G110/G32/G102/G97/G99/G116/G111/G114/G115/G32/G115/G111/G32/G116/G104/G97/G116/G32/G116/G104/G101/G32/G112/G114/G111/G98/G108/G101/G109/G32/G105/G115/G32/G109/G97/G110/G97/G103/G101/G97/G98/G108/G101/G46
/G70/G111/G114/G32/G101/G120/G97/G109/G112/G108/G101/G44/G32/G115/G117/G112/G112/G111/G115/G101/G32/G111/G117/G114/G32/G112/G114/G111/G98/G108/G101/G109/G32/G105/G115/G32/G116/G111/G32/G101/G115/G116/G105/G109/G97/G116/G101/G32/G116/G104/G101/G32/G110/G117/G109/G98/G101/G114/G32/G111/G102/G32/G102/G105/G115/G104/G101/G115/G32/G105/G110/G32/G97/G32/G108/G97/G107/G101/G46/G32/G73/G116/G32/G105/G115
/G110/G111/G116/G32/G112/G111/G115/G115/G105/G98/G108/G101/G32/G116/G111/G32/G99/G97/G112/G116/G117/G114/G101/G32/G101/G97/G99/G104/G32/G111/G102/G32/G116/G104/G101/G115/G101/G32/G102/G105/G115/G104/G101/G115/G32/G97/G110/G100/G32/G99/G111/G117/G110/G116/G32/G116/G104/G101/G109/G46/G32/G87/G101/G32/G99/G111/G117/G108/G100/G32/G112/G111/G115/G115/G105/G98/G108/G121/G32/G99/G97/G112/G116/G117/G114/G101
/G97/G32/G115/G97/G109/G112/G108/G101/G32/G97/G110/G100/G32/G102/G114/G111/G109/G32/G105/G116/G32/G116/G114/G121/G32/G97/G110/G100/G32/G101/G115/G116/G105/G109/G97/G116/G101/G32/G116/G104/G101/G32/G116/G111/G116/G97/G108/G32/G110/G117/G109/G98/G101/G114/G32/G111/G102/G32/G102/G105/G115/G104/G101/G115/G32/G105/G110/G32/G116/G104/G101/G32/G108/G97/G107/G101/G46
/G83/G116/G101/G112/G32/G50/G32/G40/G77/G97/G116/G104/G101/G109/G97/G116/G105/G99/G97/G108/G32/G100/G101/G115/G99/G114/G105/G112/G116/G105/G111/G110/G32/G97/G110/G100/G32/G102/G111/G114/G109/G117/G108/G97/G116/G105/G111/G110/G41/G32/G58/G32/G68/G101/G115/G99/G114/G105/G98/G101/G44/G32/G105/G110/G32 /G109/G97/G116/G104/G101/G109/G97/G116/G105/G99/G97/G108
/G116/G101/G114/G109/G115/G44/G32/G116/G104/G101/G32/G100/G105/G102/G102/G101/G114/G101/G110/G116/G32/G97/G115/G112/G101/G99/G116/G115/G32/G111/G102/G32/G116/G104/G101/G32/G112/G114/G111/G98/G108/G101/G109/G46/G32/G83/G111/G109/G101/G32/G119/G97/G121/G115/G32/G116/G111/G32/G100/G101/G115/G99/G114/G105/G98/G101/G32/G116/G104/G101/G32/G102/G101/G97/G116/G117/G114/G101/G115
/G109/G97/G116/G104/G101/G109/G97/G116/G105/G99/G97/G108/G108/G121/G44/G32/G105/G110/G99/G108/G117/G100/G101/G58
/G108/G100/G101/G102/G105/G110/G101/G32/G118/G97/G114/G105/G97/G98/G108/G101/G115
/G108/G119/G114/G105/G116/G101/G32/G101/G113/G117/G97/G116/G105/G111/G110/G115/G32/G111/G114/G32/G105/G110/G101/G113/G117/G97/G108/G105/G116/G105/G101/G115
/G108/G103/G97/G116/G104/G101/G114/G32/G100/G97/G116/G97/G32/G97/G110/G100/G32/G111/G114/G103/G97/G110/G105/G115/G101/G32/G105/G110/G116/G111/G32/G116/G97/G98/G108/G101/G115
/G108/G109/G97/G107/G101/G32/G103/G114/G97/G112/G104/G115
/G108/G99/G97/G108/G99/G117/G108/G97/G116/G101/G32/G112/G114/G111/G98/G97/G98/G105/G108/G105/G116/G105/G101/G115
```

### 3. pypdfium2 (Current)
```text
 
12 5	'	
		
		
12 4		'	
	

12 5	'	
			
12 4		'	
	
12 4		'	
				
	
	
12 4		'	
				
	
12 4		'	
			
 /
)	

	$
		
	
	'	
	
$				
) 	66$	
	
'
	
	'') 	67$	
) 	68$		
		
	
'
			
	
$	$		$
$

	
	
	,$#$	$
	
				
$	
	')

'
''	
$
 	
		
)")*$	
'&	
'
'
			
	
		%9	-		

		
	'




	

&	
$'
		
	
	$
		 '	
''			
		
'
3				

)	
			
	

		
(	
					
		
	



	


	

&	
	
		
 	 	 	
   $	 	
 	
	
	0
 
 $	-	-	
 '	
	'		
 '

 		
```

---

## Sample 22 [CHUNK_ID: chk_a6a8b4ed42932395]
**Document:** STD-10/Std-10_Science_English Medium.pdf | **Page:** 147

### 1. PyMuPDF (fitz)
```text
Science
134
Light – Reflection and
Refraction
9
CHAPTER
W
e see a variety of objects in the world around us. However, we are
unable to see anything in a dark room. On lighting up the room,
things become visible. What makes things visible? During the day, the
sunlight helps us to see objects. An object reflects light that falls on it.
This reflected light, when received by our eyes, enables us to see things.
We are able to see through a transparent medium as light is transmitted
through it. There are a number of common wonderful phenomena
associated with light such as image formation by mirrors, the twinkling
of stars, the beautiful colours of a rainbow, bending of light by a medium
and so on.  A study of the properties of light helps us to explore them.
By observing the common optical phenomena around us, we may
conclude that light seems to travel in straight lines. The fact that a small
source of light casts a sharp shadow of an opaque object points to this
straight-line path of light, usually indicated as a ray of light.
More to Know!
If an opaque object on the path of light becomes very small, light has a tendency to
bend around it and not walk in a straight line – an effect known as the diffraction of
light. Then the straight-line treatment of optics using rays fails. To explain phenomena
such as diffraction, light is thought of as a wave, the details of which you will study
in higher classes. Again, at the beginning of the 20th century, it became known that
the wave theory of light often becomes inadequate for treatment of the interaction of
light with matter, and light often behaves somewhat like a stream of particles. This
confusion about the true nature of light continued for some years till a modern
quantum theory of light emerged in which light is neither a ‘wave’ nor a ‘particle’ –
the new theory reconciles the particle properties of light with the wave nature.
In this Chapter, we shall study the phenomena of reflection and
refraction of light using the straight-line propagation of light. These basic
concepts will help us in the study of some of the optical phenomena in
nature. We shall try to understand in this Chapter the reflection of light
by spherical mirrors and refraction of light and their application in real
life situations.
9.1 REFLECTION OF LIGHT
9.1 REFLECTION OF LIGHT
9.1 REFLECTION OF LIGHT
9.1 REFLECTION OF LIGHT
9.1 REFLECTION OF LIGHT
A highly polished surface, such as a mirror, reflects most of the light
falling on it. You are already familiar with the laws of reflection of light.
```

### 2. pypdf (Native)
```text
Science134
Light – Reflection and
Refraction
9CHAPTER
W
e see a variety of objects in the world ar
ound us. However, we are
unable to see anything in a dark room. On lighting up the room,
things become visible. What makes things visible? During the day, the
sunlight helps us to see objects. An object reflects light that falls on it.
This reflected light, when received by our eyes, enables us to see things.
We are able to see through a transparent medium as light is transmitted
through it. There are a number of common wonderful phenomena
associated with light such as image formation by mirrors, the twinkling
of stars, the beautiful colours of a rainbow, bending of light by a medium
and so on.  A study of the properties of light helps us to explore them.
By observing the common optical phenomena around us, we may
conclude that light seems to travel in straight lines. The fact that a small
source of light casts a sharp shadow of an opaque object points to this
straight-line path of light, usually indicated as a ray of light.
More to Know!
If an opaque object on the path of light becomes very small, light has a tendency to
bend around it and not walk in a straight line – an effect known as the diffraction of
light. Then the straight-line treatment of optics using rays fails. To explain phenomena
such as diffraction, light is thought of as a wave, the details of which you will study
in higher classes. Again, at the beginning of the 20th century, it became known that
the wave theory of light often becomes inadequate for treatment of the interaction of
light with matter, and light often behaves somewhat like a stream of particles. This
confusion about the true nature of light continued for some years till a modern
quantum theory of light emerged in which light is neither a ‘wave’ nor a ‘particle’ –
the new theory reconciles the particle properties of light with the wave nature.
In this Chapter, we shall study the phenomena of r eflection and
refraction of light using the straight-line propagation of light. These basic
concepts will help us in the study of some of the optical phenomena in
nature. We shall try to understand in this Chapter the reflection of light
by spherical mirrors and refraction of light and their application in real
life situations.
9.1 REFLECTION OF LIGHT9.1 REFLECTION OF LIGHT9.1 REFLECTION OF LIGHT9.1 REFLECTION OF LIGHT9.1 REFLECTION OF LIGHT
A highly polished surface, such as a mirror, reflects most of the light
falling on it. You are already familiar with the laws of reflection of light.
```

### 3. pypdfium2 (Current)
```text
134 Science
Light – Reflection and
Refraction
CHAPTER9
We see a variety of objects in the world around us. However, we are
unable to see anything in a dark room. On lighting up the room,
things become visible. What makes things visible? During the day, the
sunlight helps us to see objects. An object reflects light that falls on it.
This reflected light, when received by our eyes, enables us to see things.
We are able to see through a transparent medium as light is transmitted
through it. There are a number of common wonderful phenomena
associated with light such as image formation by mirrors, the twinkling
of stars, the beautiful colours of a rainbow, bending of light by a medium
and so on. A study of the properties of light helps us to explore them.
By observing the common optical phenomena around us, we may
conclude that light seems to travel in straight lines. The fact that a small
source of light casts a sharp shadow of an opaque object points to this
straight-line path of light, usually indicated as a ray of light.
More to Know!
If an opaque object on the path of light becomes very small, light has a tendency to
bend around it and not walk in a straight line – an effect known as the diffraction of
light. Then the straight-line treatment of optics using rays fails. To explain phenomena
such as diffraction, light is thought of as a wave, the details of which you will study
in higher classes. Again, at the beginning of the 20th century, it became known that
the wave theory of light often becomes inadequate for treatment of the interaction of
light with matter, and light often behaves somewhat like a stream of particles. This
confusion about the true nature of light continued for some years till a modern
quantum theory of light emerged in which light is neither a ‘wave’ nor a ‘particle’ –
the new theory reconciles the particle properties of light with the wave nature.
In this Chapter, we shall study the phenomena of reflection and
refraction of light using the straight-line propagation of light. These basic
concepts will help us in the study of some of the optical phenomena in
nature. We shall try to understand in this Chapter the reflection of light
by spherical mirrors and refraction of light and their application in real
life situations.
9.1 REFLECTION OF LIGHT
A highly polished surface, such as a mirror, reflects most of the light
falling on it. You are already familiar with the laws of reflection of light.
```

---

## Sample 23 [CHUNK_ID: chk_526317bd9d86642b]
**Document:** STD-10/Std-10_Science_English Medium.pdf | **Page:** 40

### 1. PyMuPDF (fitz)
```text
Acids, Bases and Salts
27
What is the pH of the soil in your backyard?
Plants require a specific pH range for their healthy growth. To find out
the pH required for the healthy growth of a plant, you can collect the soil
from various places and check the pH in the manner described below in
Activity 2.12. Also, you can note down which plants are growing in the
region from which you have collected the soil.
Acids in other planets
The atmosphere of venus is made up of thick white and yellowish clouds of
sulphuric acid. Do you think life can exist on this planet?
Activity 2.12
Activity 2.12
Activity 2.12
Activity 2.12
Activity 2.12
n
Put about 2 g soil in a test tube and add 5 mL water to it.
n
Shake the contents of the test tube.
n
Filter the contents and collect the filtrate in a test tube.
n
Check the pH of this filtrate with the help of universal
indicator paper.
n
What can you conclude about the ideal soil pH for the growth of
plants in your region?
pH in our digestive system
It is very interesting to note that our stomach produces hydrochloric
acid. It helps in the digestion of food without harming the stomach.
During indigestion the stomach produces too much acid and this causes
pain and irritation. To get rid of this pain, people use bases called
antacids. One such remedy must have been suggested by you at the
beginning of this Chapter. These antacids neutralise the excess acid.
Magnesium hydroxide (Milk of magnesia), a mild base, is often used for
this purpose.
pH change as the cause of tooth decay
Tooth decay starts when the pH of the mouth is lower than 5.5. Tooth
enamel, made up of calcium hydroxyapatite (a crystalline form of calcium
phosphate) is the hardest substance in the body. It does not dissolve in
water, but is corroded when the pH in the mouth is below 5.5. Bacteria
present in the mouth produce acids by degradation of sugar and food
particles remaining in the mouth after eating. The best way to prevent
this is to clean the mouth after eating food. Using toothpastes, which are
generally basic, for cleaning the teeth can neutralise the excess acid and
prevent tooth decay.
Self defence by animals and plants through chemical warfare
Have you ever been stung by a honey-bee? Bee-sting leaves an acid
which  causes pain and irritation. Use of a mild base like baking soda
on the stung area gives relief. Stinging hair of nettle leaves inject
methanoic acid causing burning pain.
Do You
Know?
```

### 2. pypdf (Native)
```text
Acids, Bases and Salts 27
What is the pH of the soil in your backyard?
Plants require a specific pH range for their healthy growth. To find out
the pH required for the healthy growth of a plant, you can collect the soil
from various places and check the pH in the manner described below in
Activity 2.12. Also, you can note down which plants are growing in the
region from which you have collected the soil.
Acids in other planets
The atmosphere of venus is made up of thick white and yellowish clouds of
sulphuric acid. Do you think life can exist on this planet?
Activity 2.12Activity 2.12Activity 2.12Activity 2.12Activity 2.12
/square6Put about 2 g soil in a test tube and add 5 mL water to it.
/square6Shake the contents of the test tube.
/square6Filter the contents and collect the filtrate in a test tube.
/square6Check the pH of this filtrate with the help of universal
indicator paper .
/square6What can you conclude about the ideal soil pH for the growth of
plants in your region?
pH in our digestive system
It is very interesting to note that our stomach produces hydrochloric
acid. It helps in the digestion of food without harming the stomach.
During indigestion the stomach produces too much acid and this causes
pain and irritation. To get rid of this pain, people use bases called
antacids. One such remedy must have been suggested by you at the
beginning of this Chapter. These antacids neutralise the excess acid.
Magnesium hydroxide (Milk of magnesia), a mild base, is often used for
this purpose.
pH change as the cause of tooth decay
Tooth decay starts when the pH of the mouth is lower than 5.5. Tooth
enamel, made up of calcium hydroxyapatite (a crystalline form of calcium
phosphate) is the hardest substance in the body. It does not dissolve in
water, but is corroded when the pH in the mouth is below 5.5. Bacteria
present in the mouth produce acids by degradation of sugar and food
particles remaining in the mouth after eating. The best way to prevent
this is to clean the mouth after eating food. Using toothpastes, which are
generally basic, for cleaning the teeth can neutralise the excess acid and
prevent tooth decay.
Self defence by animals and plants through chemical warfare
Have you ever been stung by a honey-bee? Bee-sting leaves an acid
which  causes pain and irritation. Use of a mild base like baking soda
on the stung area gives relief. Stinging hair of nettle leaves inject
methanoic acid causing burning pain.
Do You
Know?
```

### 3. pypdfium2 (Current)
```text
Acids, Bases and Salts 27
What is the pH of the soil in your backyard?
Plants require a specific pH range for their healthy growth. To find out
the pH required for the healthy growth of a plant, you can collect the soil
from various places and check the pH in the manner described below in
Activity 2.12. Also, you can note down which plants are growing in the
region from which you have collected the soil.
Acids in other planets
The atmosphere of venus is made up of thick white and yellowish clouds of
sulphuric acid. Do you think life can exist on this planet?
Activity 2.12
n Put about 2 g soil in a test tube and add 5 mL water to it.
n Shake the contents of the test tube.
n Filter the contents and collect the filtrate in a test tube.
n Check the pH of this filtrate with the help of universal
indicator paper.
n What can you conclude about the ideal soil pH for the growth of
plants in your region?
pH in our digestive system
It is very interesting to note that our stomach produces hydrochloric
acid. It helps in the digestion of food without harming the stomach.
During indigestion the stomach produces too much acid and this causes
pain and irritation. To get rid of this pain, people use bases called
antacids. One such remedy must have been suggested by you at the
beginning of this Chapter. These antacids neutralise the excess acid.
Magnesium hydroxide (Milk of magnesia), a mild base, is often used for
this purpose.
pH change as the cause of tooth decay
Tooth decay starts when the pH of the mouth is lower than 5.5. Tooth
enamel, made up of calcium hydroxyapatite (a crystalline form of calcium
phosphate) is the hardest substance in the body. It does not dissolve in
water, but is corroded when the pH in the mouth is below 5.5. Bacteria
present in the mouth produce acids by degradation of sugar and food
particles remaining in the mouth after eating. The best way to prevent
this is to clean the mouth after eating food. Using toothpastes, which are
generally basic, for cleaning the teeth can neutralise the excess acid and
prevent tooth decay.
Self defence by animals and plants through chemical warfare
Have you ever been stung by a honey-bee? Bee-sting leaves an acid
which causes pain and irritation. Use of a mild base like baking soda
on the stung area gives relief. Stinging hair of nettle leaves inject
methanoic acid causing burning pain. Do You Know?
```

---

## Sample 24 [CHUNK_ID: chk_de42047b22cd274e]
**Document:** STD-10/Std-10_Maths_EnglishMedium.pdf | **Page:** 15

### 1. PyMuPDF (fitz)
```text

	
	
	
	
0!
#!		G
0	D
). 
	!
		
					

	
 	
6<
). 
	


				
	
  


<
). 



#	 !	!	 	!
0	<
). 

!	
#	



<
). 



!		






 


0		 	 	
	 		 	


	
	#		<

	
 
!
	 	!


<
).

##		 



	<
) . 

	
##	
		 

	#		
#
	

	#	 <
). 
#
						
	/	!

<
)	.

 	
!
$#	
<
)$.

	#
"	
		#	
	#
	#	!
	

!	
	 #
#

	#<
O). 
	
 	

#	

		
	

		
! 
	"

!
 	

						

 !"#	$$
$%&!""'
()			*#
 ++	$$
$
,	++'
 	

```

### 2. pypdf (Native)
```text
/G120/G105/G105
/G67/G111/G110/G115/G116/G105/G116/G117/G116/G105/G111/G110/G32/G111/G102/G32/G73/G110/G100/G105/G97
/G70/G117/G110/G100/G97/G109/G101/G110/G116/G97/G108/G32 /G68/G117/G116/G105/G101/G115
/G73/G116/G32/G115/G104/G97/G108/G108/G32/G98/G101/G32/G116/G104/G101/G32/G100/G117/G116/G121/G32/G111/G102/G32/G101/G118/G101/G114/G121/G32/G99/G105/G116/G105/G122/G101/G110/G32/G111/G102/G32/G73/G110/G100/G105/G97/G32/G151
/G40/G97/G41 /G116/G111/G32/G97/G98/G105/G100/G101/G32/G98/G121/G32/G116/G104/G101/G32/G67/G111/G110/G115/G116/G105/G116/G117/G116/G105/G111/G110/G32/G97/G110/G100/G32/G114/G101/G115/G112/G101/G99/G116/G32/G105/G116/G115/G32/G105/G100/G101/G97/G108/G115/G32/G97/G110/G100/G32/G105/G110/G115/G116/G105/G116/G117/G116/G105/G111/G110/G115/G44/G32/G116/G104/G101
/G78/G97/G116/G105/G111/G110/G97/G108/G32/G70/G108/G97/G103/G32/G97/G110/G100/G32/G116/G104/G101/G32/G78/G97/G116/G105/G111/G110/G97/G108/G32/G65/G110/G116/G104/G101/G109/G59
/G40/G98/G41 /G116/G111/G32/G99/G104/G101/G114/G105/G115/G104/G32/G97/G110/G100/G32/G102/G111/G108/G108/G111/G119/G32/G116/G104/G101/G32/G110/G111/G98/G108/G101/G32/G105/G100/G101/G97/G108/G115/G32/G119/G104/G105/G99/G104/G32/G105/G110/G115/G112/G105/G114/G101/G100/G32/G111/G117/G114/G32/G110/G97/G116/G105/G111/G110/G97/G108/G32/G115/G116/G114/G117/G103/G103/G108/G101
/G102/G111/G114/G32/G102/G114/G101/G101/G100/G111/G109/G59
/G40/G99/G41 /G116/G111/G32/G117/G112/G104/G111/G108/G100/G32/G97/G110/G100/G32/G112/G114/G111/G116/G101/G99/G116/G32/G116/G104/G101/G32/G115/G111/G118/G101/G114/G101/G105/G103/G110/G116/G121/G44/G32/G117/G110/G105/G116/G121/G32/G97/G110/G100/G32/G105/G110/G116/G101/G103/G114/G105/G116/G121/G32/G111/G102/G32/G73/G110/G100/G105/G97/G59
/G40/G100/G41 /G116/G111/G32/G100/G101/G102/G101/G110/G100/G32/G116/G104/G101/G32/G99/G111/G117/G110/G116/G114/G121/G32/G97/G110/G100/G32/G114/G101/G110/G100/G101/G114/G32/G110/G97/G116/G105/G111/G110/G97/G108/G32/G115/G101/G114/G118/G105/G99/G101/G32/G119/G104/G101/G110/G32/G99/G97/G108/G108/G101/G100/G32/G117/G112/G111/G110/G32/G116/G111
/G100/G111/G32/G115/G111/G59
/G40/G101/G41 /G116/G111/G32/G112/G114/G111/G109/G111/G116/G101/G32/G104/G97/G114/G109/G111/G110/G121/G32/G97/G110/G100/G32/G116/G104/G101/G32/G115/G112/G105/G114/G105/G116/G32/G111/G102/G32/G99/G111/G109/G109/G111/G110/G32/G98/G114/G111/G116/G104/G101/G114/G104/G111/G111/G100/G32/G97/G109/G111/G110/G103/G115/G116/G32/G97/G108/G108
/G116/G104/G101/G32/G112/G101/G111/G112/G108/G101/G32/G111/G102/G32/G73/G110/G100/G105/G97/G32/G116/G114/G97/G110/G115/G99/G101/G110/G100/G105/G110/G103/G32/G114/G101/G108/G105/G103/G105/G111/G117/G115/G44/G32/G108/G105/G110/G103/G117/G105/G115/G116/G105/G99/G32/G97/G110/G100/G32/G114/G101/G103/G105/G111/G110/G97/G108/G32/G111/G114
/G115/G101/G99/G116/G105/G111/G110/G97/G108/G32/G100/G105/G118/G101/G114/G115/G105/G116/G105/G101/G115/G59/G32/G116/G111/G32/G114/G101/G110/G111/G117/G110/G99/G101/G32/G112/G114/G97/G99/G116/G105/G99/G101/G115/G32/G100/G101/G114/G111/G103/G97/G116/G111/G114/G121/G32/G116/G111/G32/G116/G104/G101/G32/G100/G105/G103/G110/G105/G116/G121/G32/G111/G102
/G119/G111/G109/G101/G110/G59
/G40/G102/G41 /G116/G111/G32/G118/G97/G108/G117/G101/G32/G97/G110/G100/G32/G112/G114/G101/G115/G101/G114/G118/G101/G32/G116/G104/G101/G32/G114/G105/G99/G104/G32/G104/G101/G114/G105/G116/G97/G103/G101/G32/G111/G102/G32/G111/G117/G114/G32/G99/G111/G109/G112/G111/G115/G105/G116/G101/G32/G99/G117/G108/G116/G117/G114/G101/G59
/G40/G103/G41 /G116/G111/G32/G112/G114/G111/G116/G101/G99/G116/G32/G97/G110/G100/G32/G105/G109/G112/G114/G111/G118/G101/G32/G116/G104/G101/G32/G110/G97/G116/G117/G114/G97/G108/G32/G101/G110/G118/G105/G114/G111/G110/G109/G101/G110/G116/G32/G105/G110/G99/G108/G117/G100/G105/G110/G103/G32/G102/G111/G114/G101/G115/G116/G115/G44/G32/G108/G97/G107/G101/G115/G44
/G114/G105/G118/G101/G114/G115/G44/G32/G119/G105/G108/G100/G108/G105/G102/G101/G32/G97/G110/G100/G32/G116/G111/G32/G104/G97/G118/G101/G32/G99/G111/G109/G112/G97/G115/G115/G105/G111/G110/G32/G102/G111/G114/G32/G108/G105/G118/G105/G110/G103/G32/G99/G114/G101/G97/G116/G117/G114/G101/G115/G59
/G40/G104/G41 /G116/G111/G32/G100/G101/G118/G101/G108/G111/G112/G32/G116/G104/G101/G32/G115/G99/G105/G101/G110/G116/G105/G102/G105/G99/G32/G116/G101/G109/G112/G101/G114/G44/G32/G104/G117/G109/G97/G110/G105/G115/G109/G32/G97/G110/G100/G32/G116/G104/G101/G32/G115/G112/G105/G114/G105/G116/G32/G111/G102/G32/G105/G110/G113/G117/G105/G114/G121/G32/G97/G110/G100
/G114/G101/G102/G111/G114/G109/G59
/G40/G105/G41 /G116/G111/G32/G115/G97/G102/G101/G103/G117/G97/G114/G100/G32/G112/G117/G98/G108/G105/G99/G32/G112/G114/G111/G112/G101/G114/G116/G121/G32/G97/G110/G100/G32/G116/G111/G32/G97/G98/G106/G117/G114/G101/G32/G118/G105/G111/G108/G101/G110/G99/G101/G59
/G40/G106/G41 /G116/G111/G32/G115/G116/G114/G105/G118/G101/G32/G116/G111/G119/G97/G114/G100/G115/G32/G101/G120/G99/G101/G108/G108/G101/G110/G99/G101/G32/G105/G110/G32/G97/G108/G108/G32/G115/G112/G104/G101/G114/G101/G115/G32/G111/G102/G32/G105/G110/G100/G105/G118/G105/G100/G117/G97/G108/G32/G97/G110/G100/G32/G99/G111/G108/G108/G101/G99/G116/G105/G118/G101
/G97/G99/G116/G105/G118/G105/G116/G121/G32/G115/G111/G32/G116/G104/G97/G116/G32/G116/G104/G101/G32/G110/G97/G116/G105/G111/G110/G32/G99/G111/G110/G115/G116/G97/G110/G116/G108/G121/G32/G114/G105/G115/G101/G115/G32/G116/G111/G32/G104/G105/G103/G104/G101/G114/G32/G108/G101/G118/G101/G108/G115/G32/G111/G102/G32/G101/G110/G100/G101/G97/G118/G111/G117/G114
/G97/G110/G100/G32/G97/G99/G104/G105/G101/G118/G101/G109/G101/G110/G116/G59
/G42/G40/G107/G41 /G119/G104/G111/G32/G105/G115/G32/G97/G32/G112/G97/G114/G101/G110/G116/G32/G111/G114/G32/G103/G117/G97/G114/G100/G105/G97/G110/G44/G32/G116/G111/G32/G112/G114/G111/G118/G105/G100/G101/G32/G111/G112/G112/G111/G114/G116/G117/G110/G105/G116/G105/G101/G115/G32/G102/G111/G114/G32/G101/G100/G117/G99/G97/G116/G105/G111/G110/G32/G116/G111
/G104/G105/G115/G32/G99/G104/G105/G108/G100/G32/G111/G114/G44/G32/G97/G115/G32/G116/G104/G101/G32/G99/G97/G115/G101/G32/G109/G97/G121/G32/G98/G101/G44/G32/G119/G97/G114/G100/G32/G98/G101/G116/G119/G101/G101/G110/G32/G116/G104/G101/G32/G97/G103/G101/G32/G111/G102/G32/G115/G105/G120/G32/G97/G110/G100
/G102/G111/G117/G114/G116/G101/G101/G110/G32/G121/G101/G97/G114/G115/G46
/G78/G111/G116/G101/G58/G84/G104/G101/G32/G65/G114/G116/G105/G99/G108/G101/G32 /G53/G49/G65/G32 /G99/G111/G110/G116/G97/G105/G110/G105/G110/G103/G32 /G70/G117/G110/G100/G97/G109/G101/G110/G116/G97/G108/G32 /G68/G117/G116/G105/G101/G115/G32 /G119/G97/G115/G32 /G105/G110/G115/G101/G114/G116/G101/G100/G32 /G98/G121/G32 /G116/G104/G101/G32 /G67/G111/G110/G115/G116/G105/G116/G117/G116/G105/G111/G110
/G40/G52/G50/G110/G100/G32/G65/G109/G101/G110/G100/G109/G101/G110/G116/G41/G32/G65/G99/G116/G44/G32/G49/G57/G55/G54/G32/G40/G119/G105/G116/G104/G32/G101/G102/G102/G101/G99/G116/G32/G102/G114/G111/G109/G32/G51/G32/G74/G97/G110/G117/G97/G114/G121/G32/G49/G57/G55/G55/G41/G46
/G42/G40/G107/G41/G32/G119/G97/G115/G32/G105/G110/G115/G101/G114/G116/G101/G100/G32/G98/G121/G32/G116/G104/G101/G32/G67/G111/G110/G115/G116/G105/G116/G117/G116/G105/G111/G110/G32/G40/G56/G54/G116/G104/G32/G65/G109/G101/G110/G100/G109/G101/G110/G116/G41/G32/G65/G99/G116/G44/G32/G50/G48/G48/G50/G32/G40/G119/G105/G116/G104/G32/G101/G102/G102/G101/G99/G116/G32/G102/G114/G111/G109
/G49/G32/G65/G112/G114/G105/G108/G32/G50/G48/G49/G48/G41/G46
/c80/c97/c114/c116/c32/c73/c86/c32/c65/c32/c40/c65/c114/c116/c105/c99/c108/c101/c32/c53/c49/c32/c65/c41
```

### 3. pypdfium2 (Current)
```text

	
	
	
 	
0!
#!		G
0	D
). 
	!
		
					

	
 	
6<
). 
	


				
	
 


<
). 



#	 !	!	 	!
0	<
). 

!	
#	




<
). 



!		






 


0		 	 	
	 		 	


	
	#		<

	
 
!
	 	!


<
). 
##		 



	<
) . 

	
##	
		 

	#		
#
	

	#	 <
). 
#
						
	/	!

<
)	. 
 	
!
$#	
<
)$. 
	#
"	
		#	
	#
	#	!
	

!	
	 #
#

	#<
O). 
	
 	

#	

		
	


	 	 
  !      
 	" 

!
 	
  
		  	 	 		

 !"#	$$
$%&!""'
()			*#
 ++	$$
$
,	++'
	
 
```

---

## Sample 25 [CHUNK_ID: chk_13393e8e96a7b390]
**Document:** STD-10/Std-10_Maths_EnglishMedium.pdf | **Page:** 183

### 1. PyMuPDF (fitz)
```text
3
	
) 	


	



  	





		


.	

5;?
 	
$	
		

;


5
* 4
 	0 	
1 1
2  		

0
3
1
22
7
7
15
7
8
15 m
2
7
2
2
⎡
⎤
×
×
+
×
×
×
×
⎢
⎥
⎣
⎦
0?;5
.7	

0&>>
$	
0>=>>?09
) 	


0 ?;5:&>>>>19>0?;5
  $ %
 		   
 


	

&
)

	

		
5       	  


	




	!
	
>


	
	
Eπ0&/
*


	05
0>

	0 π	
0 &/=5=5=>0C95
F	
	
	 	

	




	 2
3 π	
3
2
3.14
2.5
2.5
2.5 cm
3 ×
×
×
×
0&;
* 	
	0 
	: 	


0 C95:&;
0 9&5/

```

### 2. pypdf (Native)
```text
/G49/G54/G56 /G77/G65 /G84/G72/G69/G77/G65 /G84/G73/G67/G83
/G83/G111/G108/G117/G116/G105/G111/G110/G32/G58/G32/G84/G104/G101/G32/G118/G111/G108/G117/G109/G101/G32/G111/G102/G32/G97/G105/G114/G32/G105/G110/G115/G105/G100/G101/G32/G116/G104/G101/G32/G115/G104/G101/G100/G32/G40/G119/G104/G101/G110/G32/G116/G104/G101/G114/G101/G32/G97/G114/G101/G32/G110/G111/G32/G112/G101/G111/G112/G108/G101/G32/G111/G114/G32/G109/G97/G99/G104/G105/G110/G101/G114/G121/G41
/G105/G115/G32
/G103/G105/G118/G101/G110/G32/G98/G121/G32/G116/G104/G101/G32/G118/G111/G108/G117/G109/G101/G32/G111/G102/G32/G97/G105/G114/G32/G105/G110/G115/G105/G100/G101/G32/G116/G104/G101/G32/G99/G117/G98/G111/G105/G100/G32/G97/G110/G100/G32/G105/G110/G115/G105/G100/G101/G32/G116/G104/G101/G32/G104/G97/G108/G102/G32/G99/G121/G108/G105/G110/G100/G101/G114/G44/G32/G116/G97/G107/G101/G110
/G116/G111/G103/G101/G116/G104/G101/G114/G46
/G78/G111/G119/G44/G32/G116/G104/G101/G32/G108/G101/G110/G103/G116/G104/G44/G32/G98/G114/G101/G97/G100/G116/G104/G32/G97/G110/G100/G32/G104/G101/G105/G103/G104/G116/G32/G111/G102/G32/G116/G104/G101/G32/G99/G117/G98/G111/G105/G100/G32/G97/G114/G101/G32/G49/G53/G32/G109/G44/G32/G55/G32/G109/G32/G97/G110/G100/G32/G56/G32/G109/G44/G32/G114/G101/G115/G112/G101/G99/G116/G105/G118/G101/G108/G121/G46
/G65/G108/G115/G111/G44/G32/G116/G104/G101/G32/G100/G105/G97/G109/G101/G116/G101/G114/G32/G111/G102/G32/G116/G104/G101/G32/G104/G97/G108/G102/G32/G99/G121/G108/G105/G110/G100/G101/G114/G32/G105/G115/G32/G55/G32/G109/G32/G97/G110/G100/G32/G105/G116/G115/G32/G104/G101/G105/G103/G104/G116/G32/G105/G115/G32/G49/G53/G32/G109/G46
/G83/G111/G44 /G116/G104/G101/G32/G114/G101/G113/G117/G105/G114/G101/G100/G32/G118/G111/G108/G117/G109/G101/G32/G61 /G118/G111/G108/G117/G109/G101/G32/G111/G102/G32/G116/G104/G101/G32/G99/G117/G98/G111/G105/G100/G32/G43/G321
2 /G32/G118/G111/G108/G117/G109/G101/G32/G111/G102/G32/G116/G104/G101/G32/G99/G121/G108/G105/G110/G100/G101/G114
/G61 312 2771 578 1 5 m 272 2
⎡⎤ ××+ × × × ×⎢⎥⎣⎦
/G32/G61/G32/G49/G49/G50/G56/G46/G55/G53/G32/G109/G51
/G78/G101/G120/G116/G44/G32/G116/G104/G101/G32/G116/G111/G116/G97/G108/G32/G115/G112/G97/G99/G101/G32/G111/G99/G99/G117/G112/G105/G101/G100/G32/G98/G121/G32/G116/G104/G101/G32/G109/G97/G99/G104/G105/G110/G101/G114/G121/G32/G61/G32/G51/G48/G48/G32/G109/G51
/G65/G110/G100/G32/G116/G104/G101/G32/G116/G111/G116/G97/G108/G32/G115/G112/G97/G99/G101/G32/G111/G99/G99/G117/G112/G105/G101/G100/G32/G98/G121/G32/G116/G104/G101/G32/G119/G111/G114/G107/G101/G114/G115/G32/G61/G32/G50/G48/G32/G215/G32/G48/G46/G48/G56/G32/G109/G51/G32/G61/G32/G49/G46/G54/G32/G109/G51
/G84/G104/G101/G114/G101/G102/G111/G114/G101/G44/G32/G116/G104/G101/G32/G118/G111/G108/G117/G109/G101/G32/G111/G102/G32/G116/G104/G101/G32/G97/G105/G114/G44/G32/G119/G104/G101/G110/G32/G116/G104/G101/G114/G101/G32/G97/G114/G101/G32/G109/G97/G99/G104/G105/G110/G101/G114/G121/G32/G97/G110/G100/G32/G119/G111/G114/G107/G101/G114/G115
/G61 /G49/G49/G50/G56/G46/G55/G53/G32/G150/G32/G40/G51/G48/G48/G46/G48/G48/G32/G43/G32/G49/G46/G54/G48/G41/G32/G61/G32/G56/G50/G55/G46/G49/G53/G32/G109/G51
/G69/G120/G97/G109/G112/G108/G101/G32 /G54/G32 /G58/G32/G65/G32/G106/G117/G105/G99/G101/G32/G115/G101/G108/G108/G101/G114/G32/G119/G97/G115/G32/G115/G101/G114/G118/G105/G110/G103/G32/G104/G105/G115
/G99/G117/G115/G116/G111/G109/G101/G114/G115/G32
/G117/G115/G105/G110/G103/G32/G103/G108/G97/G115/G115/G101/G115/G32/G97/G115/G32/G115/G104/G111/G119/G110/G32/G105/G110/G32/G70/G105/G103/G46/G32/G49/G50/G46/G49/G51/G46
/G84/G104/G101/G32/G105/G110/G110/G101/G114/G32/G100/G105/G97/G109/G101/G116/G101/G114/G32/G111/G102/G32/G116/G104/G101/G32/G99/G121/G108/G105/G110/G100/G114/G105/G99/G97/G108/G32/G103/G108/G97/G115/G115/G32/G119/G97/G115
/G53/G32/G99/G109/G44/G32/G98/G117/G116/G32/G116/G104/G101/G32/G98/G111/G116/G116/G111/G109/G32/G111/G102/G32/G116/G104/G101/G32/G103/G108/G97/G115/G115/G32/G104/G97/G100/G32/G97
/G104/G101/G109/G105/G115/G112/G104/G101/G114/G105/G99/G97/G108/G32/G114/G97/G105/G115/G101/G100/G32/G112/G111/G114/G116/G105/G111/G110/G32/G119/G104/G105/G99/G104/G32/G114/G101/G100/G117/G99/G101/G100/G32/G116/G104/G101
/G99/G97/G112/G97/G99/G105/G116/G121/G32/G111/G102/G32/G116/G104/G101/G32/G103/G108/G97/G115/G115/G46/G32/G73/G102/G32/G116/G104/G101/G32/G104/G101/G105/G103/G104/G116/G32/G111/G102/G32/G97/G32/G103/G108/G97/G115/G115
/G119/G97/G115/G32/G49/G48/G32/G99/G109/G44/G32/G102/G105/G110/G100/G32/G116/G104/G101/G32/G97/G112/G112/G97/G114/G101/G110/G116/G32/G99/G97/G112/G97/G99/G105/G116/G121/G32/G111/G102/G32/G116/G104/G101
/G103/G108/G97/G115/G115/G32/G97/G110/G100/G32/G105/G116/G115/G32/G97/G99/G116/G117/G97/G108/G32/G99/G97/G112/G97/G99/G105/G116/G121/G46/G32/G40/G85/G115/G101/G32π/G32/G61/G32/G51/G46/G49/G52/G46/G41
/G83/G111/G108/G117/G116/G105/G111/G110/G32/G58/G32/G83/G105/G110/G99/G101/G32/G116/G104/G101/G32/G105/G110/G110/G101/G114/G32/G100/G105/G97/G109/G101/G116/G101/G114/G32/G111/G102/G32/G116/G104/G101/G32/G103/G108/G97/G115/G115/G32/G61/G32/G53/G32/G99/G109/G32/G97/G110/G100/G32/G104/G101/G105/G103/G104/G116/G32/G61/G32/G49/G48/G32/G99/G109/G44
/G116/G104/G101/G32/G97/G112/G112/G97/G114/G101/G110/G116/G32
/G99/G97/G112/G97/G99/G105/G116/G121/G32/G111/G102/G32/G116/G104/G101/G32/G103/G108/G97/G115/G115/G32/G61π/G114/G50/G104
/G61 /G51/G46/G49/G52/G32/G215/G32/G50/G46/G53/G32/G215/G32/G50/G46/G53/G32/G215/G32/G49/G48/G32/G99/G109/G51/G32/G61/G32/G49/G57/G54/G46/G50/G53/G32/G99/G109/G51
/G66/G117/G116/G32/G116/G104/G101/G32/G97/G99/G116/G117/G97/G108/G32/G99/G97/G112/G97/G99/G105/G116/G121/G32/G111/G102/G32/G116/G104/G101/G32/G103/G108/G97/G115/G115/G32/G105/G115/G32/G108/G101/G115/G115/G32/G98/G121/G32/G116/G104/G101/G32/G118/G111/G108/G117/G109/G101/G32/G111/G102/G32/G116/G104/G101/G32/G104/G101/G109/G105/G115/G112/G104/G101/G114/G101/G32/G97/G116/G32/G116/G104/G101
/G98/G97/G115/G101/G32/G111/G102/G32/G116/G104/G101/G32/G103/G108/G97/G115/G115/G46
/G105/G46/G101/G46/G44 /G105/G116/G32/G105/G115/G32/G108/G101/G115/G115/G32/G98/G121/G322
3 /G32π/G114/G51/G32/G61
32 3.14 2.5 2.5 2.5 cm3 × ××× /G32/G61/G32/G51/G50/G46/G55/G49/G32/G99/G109/G51
/G83/G111/G44 /G116/G104/G101/G32/G97/G99/G116/G117/G97/G108/G32/G99/G97/G112/G97/G99/G105/G116/G121/G32/G111/G102/G32/G116/G104/G101/G32/G103/G108/G97/G115/G115/G32/G61 /G97/G112/G112/G97/G114/G101/G110/G116/G32/G99/G97/G112/G97/G99/G105/G116/G121/G32/G111/G102/G32/G103/G108/G97/G115/G115/G32/G150/G32/G118/G111/G108/G117/G109/G101/G32/G111/G102/G32/G116/G104/G101
/G104/G101/G109/G105/G115/G112/G104/G101/G114/G101
/G61 /G40/G49/G57/G54/G46/G50/G53/G32/G150/G32/G51/G50/G46/G55/G49/G41/G32/G99/G109/G51
/G61 /G49/G54/G51/G46/G53/G52/G32/G99/G109/G51
/G70/G105/G103/G46/G32 /G49/G50/G46/G49/G51
```

### 3. pypdfium2 (Current)
```text
3 	
 ) 	


	



  	





		


.	

5;?
 	
$	
		

;


5
* 4
 	0 	
1
1
2  		

0 1 22 7 7 3 15 7 8 15 m
2 7 22
⎡⎤ ××+ × × × × ⎢⎥ ⎣⎦ 0?;5
.7	

0&>>
$	
0>=>>?09
) 	


0 ?;5:&>>>>19>0?;5
   $ %
 		   
 


	

&
)

	

		
5     	  


	




	!
	
>


	
	
Eπ0&/
 *


	05
0>

	0 π	 
0 &/=5=5=>
0C95
F	
	
	 	

	

 

	
2
3 π	

2 3 3.14 2.5 2.5 2.5 cm
3
× ××× 0&;
* 	
	0 
	: 	


0 C95:&;
0 9&5/
 
```

---

## Sample 26 [CHUNK_ID: chk_67815a2d1e9cf828]
**Document:** STD-10/Std-10_Science_English Medium.pdf | **Page:** 79

### 1. PyMuPDF (fitz)
```text
Science
66
bonds with other elements such as halogens, oxygen, nitrogen and sulphur.
In a hydrocarbon chain, one or more hydrogens can be replaced by these
elements, such that the valency of carbon remains satisfied. In such
compounds, the element replacing hydrogen is referred to as a heteroatom.
These heteroatoms are also present in some groups as given in Table 4.3.
These heteroatoms and
the group containing
these confer specific
properties 
to 
the
compound, regardless
of the length and nature
of the carbon chain and
hence 
are 
called
functional groups. Some
important functional
groups are given in the
Table 4.3. Free valency or
valencies of the group
are shown by the single
line. The functional group
is attached to the carbon
chain through this
valency by replacing one
hydrogen   atom or
atoms.
4.2.4 Homologous Series
You have seen that carbon atoms can be linked together to form chains
of varying lengths. These chains can be branched also. In addition,
hydrogen atom or other atoms on these carbon chains can be replaced
by any of the functional groups that we saw above. The presence of a
functional group such as alcohol decides the properties of the carbon
compound, regardless of the length of the carbon chain. For example,
the chemical properties of CH3OH, C2H5OH, C3H7OH and C4H9OH are all
very similar. Hence, such a series of compounds in which the same
functional group substitutes for hydrogen in a carbon chain is called a
homologous series.
Let us look at the homologous series that we saw earlier in Table
4.2. If we look at the formulae of successive compounds, say –
CH4 and C2H6
—
these differ by a –CH2- unit
C2H6 and C3H8
—
these differ by a –CH2- unit
What is the difference between the next pair – propane and butane (C4H10)?
Can you find out the difference in molecular masses between these
pairs (the atomic mass of carbon is 12 u and the atomic mass of hydrogen
is 1 u)?
Similarly, take the homologous series for alkenes. The first member
of the series is ethene which we have already come across in
Section 4.2.1. What is the formula for ethene? The succeeding members
have the formula C3H6, C4H8 and C5H10. Do these also differ by a –CH2–
Table 4.3 Some functional groups in carbon compounds
Hetero
Hetero
Hetero
Hetero
Hetero
Class of
Class of
Class of
Class of
Class of
Formula of
Formula of
Formula of
Formula of
Formula of
atom
atom
atom
atom
atom
compounds
compounds
compounds
compounds
compounds
functional group
functional group
functional group
functional group
functional group
Cl/Br
Halo- (Chloro/bromo)
—Cl, —Br
alkane
(substitutes for
hydrogen atom)
Oxygen
1. Alcohol
—OH
2. Aldehyde
3. Ketone
4. Carboxylic acid
```

### 2. pypdf (Native)
```text
Science66
bonds with other elements such as halogens, oxygen, nitrogen and sulphur.
In a hydrocarbon chain, one or more hydrogens can be replaced by these
elements, such that the valency of carbon remains satisfied. In such
compounds, the element replacing hydrogen is referred to as a heteroatom.
These heteroatoms are also present in some groups as given in Table 4.3.
These heteroatoms 
and
the group containing
these confer specific
properties to the
compound, regardless
of the length and nature
of the carbon chain and
hence are called
functional groups. Some
important functional
groups are given in the
Table 4.3. Free valency or
valencies of the group
are shown by the single
line. The functional group
is attached to the carbon
chain through this
valency by replacing one
hydrogen   atom or
atoms.
4.2.4 Homologous Series
You have seen that carbon atoms can be linked together to form chains
of varying lengths. These chains can be branched also. In addition,
hydrogen atom or other atoms on these carbon chains can be replaced
by any of the functional groups that we saw above. The presence of a
functional group such as alcohol decides the properties of the carbon
compound, regardless of the length of the carbon chain. For example,
the chemical properties of CH3OH, C2H5OH, C3H7OH and C4H9OH are all
very similar. Hence, such a series of compounds in which the same
functional group substitutes for hydrogen in a carbon chain is called a
homologous series.
Let us look at the homologous series that we saw earlier in Table
4.2. If we look at the formulae of successive compounds, say –
CH4 and C2H6 — these differ by a –CH2- unit
C2H6 and C3H8 — these differ by a –CH2- unit
What is the difference between the next pair – propane and butane (C4H10)?
Can you find out the difference in molecular masses between these
pairs (the atomic mass of carbon is 12 u and the atomic mass of hydrogen
is 1 u)?
Similarly, take the homologous series for alkenes. The first member
of the series is ethene which we have already come across in
Section 4.2.1. What is the formula for ethene? The succeeding members
have the formula C3H6, C4H8 and C5H10. Do these also differ by a –CH2–
Table 4.3 Some functional groups in carbon compounds
Hetero HeteroHetero HeteroHetero Class of Class ofClass of Class ofClass of Formula ofFormula ofFormula ofFormula ofFormula of
atom atomatom atomatom compoundscompoundscompoundscompoundscompounds functional groupfunctional groupfunctional groupfunctional groupfunctional group
Cl/Br Halo- (Chloro/bromo) —Cl, —Br
alkane (substitutes for
hydrogen atom)
Oxygen 1. Alcohol —OH
2. Aldehyde
3. Ketone
4. Carboxylic acid
```

### 3. pypdfium2 (Current)
```text
66 Science
bonds with other elements such as halogens, oxygen, nitrogen and sulphur.
In a hydrocarbon chain, one or more hydrogens can be replaced by these
elements, such that the valency of carbon remains satisfied. In such
compounds, the element replacing hydrogen is referred to as a heteroatom.
These heteroatoms are also present in some groups as given in Table 4.3.
These heteroatoms and
the group containing
these confer specific
properties to the
compound, regardless
of the length and nature
of the carbon chain and
hence are called
functional groups. Some
important functional
groups are given in the
Table 4.3. Free valency or
valencies of the group
are shown by the single
line. The functional group
is attached to the carbon
chain through this
valency by replacing one
hydrogen atom or
atoms.
4.2.4 Homologous Series
You have seen that carbon atoms can be linked together to form chains
of varying lengths. These chains can be branched also. In addition,
hydrogen atom or other atoms on these carbon chains can be replaced
by any of the functional groups that we saw above. The presence of a
functional group such as alcohol decides the properties of the carbon
compound, regardless of the length of the carbon chain. For example,
the chemical properties of CH3OH, C2H5OH, C3H7OH and C4H9OH are all
very similar. Hence, such a series of compounds in which the same
functional group substitutes for hydrogen in a carbon chain is called a
homologous series.
Let us look at the homologous series that we saw earlier in Table
4.2. If we look at the formulae of successive compounds, say –
CH4 and C2H6 — these differ by a –CH2- unit
C2H6 and C3H8 — these differ by a –CH2- unit
What is the difference between the next pair – propane and butane (C4H10)?
Can you find out the difference in molecular masses between these
pairs (the atomic mass of carbon is 12 u and the atomic mass of hydrogen
is 1 u)?
Similarly, take the homologous series for alkenes. The first member
of the series is ethene which we have already come across in
Section 4.2.1. What is the formula for ethene? The succeeding members
have the formula C3H6, C4H8 and C5H10. Do these also differ by a –CH2–
Table 4.3 Some functional groups in carbon compounds
Hetero Class of Class ofClass of Formula of
atom compounds functional group
Cl/Br Halo- (Chloro/bromo) —Cl, —Br
alkane (substitutes for
hydrogen atom)
Oxygen 1. Alcohol —OH
2. Aldehyde
3. Ketone
4. Carboxylic acid
```

---

## Sample 27 [CHUNK_ID: chk_0cd824449b5b72f9]
**Document:** STD-10/Std-10_Maths_EnglishMedium.pdf | **Page:** 177

### 1. PyMuPDF (fitz)
```text

	
$
 %	



&'
#$
(
	 

	
)

	

	


*

		
	 		
 


	
	



	

 
!

 	


%	
#+	

	
 	

!

		
 	
%
 	
			
,



-

	
#. 	




			 	
	 +

	

	



!	
		
 

/
		
	
!
	%		
	 
 	

*	

	



 
	)

 
)*$	
0'*$
1'*$	

 1'*$

)*$ '*$   2)	 *$3  2'  *$3

 	
,


*



,	



```

### 2. pypdf (Native)
```text
/G49/G54/G50 /G77/G65 /G84/G72/G69/G77/G65 /G84/G73/G67/G83
/G65/G103/G97/G105/G110/G44/G32/G121/G111/G117/G32/G109/G97/G121/G32/G104/G97/G118/G101/G32/G115/G101/G101/G110/G32/G97/G110/G32/G111/G98/G106/G101/G99/G116/G32/G108/G105/G107/G101/G32/G116/G104/G101
/G111/G110/G101/G32/G105/G110/G32/G70/G105/G103/G46/G32/G49/G50/G46/G51/G46/G32/G67/G97/G110/G32/G121/G111/G117/G32/G110/G97/G109/G101/G32/G105/G116/G63/G32/G65/G32/G116/G101/G115/G116/G32/G116/G117/G98/G101/G44/G32/G114/G105/G103/G104/G116/G33
/G89/G111/G117/G32/G119/G111/G117/G108/G100/G32/G104/G97/G118/G101/G32/G117/G115/G101/G100/G32/G111/G110/G101/G32/G105/G110/G32/G121/G111/G117/G114/G32/G115/G99/G105/G101/G110/G99/G101/G32/G108/G97/G98/G111/G114/G97/G116/G111/G114/G121/G46
/G84/G104/G105/G115/G32/G116/G117/G98/G101/G32/G105/G115/G32/G97/G108/G115/G111/G32/G97/G32/G99/G111/G109/G98/G105/G110/G97/G116/G105/G111/G110/G32/G111/G102/G32/G97/G32/G99/G121/G108/G105/G110/G100/G101/G114/G32/G97/G110/G100/G32/G97
/G104/G101/G109/G105/G115/G112/G104/G101/G114/G101/G46/G32/G83/G105/G109/G105/G108/G97/G114/G108/G121/G44/G32/G119/G104/G105/G108/G101/G32/G116/G114/G97/G118/G101/G108/G108/G105/G110/G103/G44/G32/G121/G111/G117/G32/G109/G97/G121/G32/G104/G97/G118/G101
/G115/G101/G101/G110/G32/G115/G111/G109/G101/G32/G98/G105/G103/G32/G97/G110/G100/G32/G98/G101/G97/G117/G116/G105/G102/G117/G108/G32/G98/G117/G105/G108/G100/G105/G110/G103/G115/G32/G111/G114/G32/G109/G111/G110/G117/G109/G101/G110/G116/G115
/G109/G97/G100/G101/G32/G117/G112/G32/G111/G102/G32/G97/G32/G99/G111/G109/G98/G105/G110/G97/G116/G105/G111/G110/G32/G111/G102/G32/G115/G111/G108/G105/G100/G115/G32/G109/G101/G110/G116/G105/G111/G110/G101/G100/G32/G97/G98/G111/G118/G101/G46
/G73/G102/G32/G102/G111/G114/G32/G115/G111/G109/G101/G32/G114/G101/G97/G115/G111/G110/G32/G121/G111/G117/G32/G119/G97/G110/G116/G101/G100/G32/G116/G111/G32/G102/G105/G110/G100/G32/G116/G104/G101
/G115/G117/G114/G102/G97/G99/G101/G32/G97/G114/G101/G97/G115/G44/G32/G111/G114/G32/G118/G111/G108/G117/G109/G101/G115/G44/G32/G111/G114/G32/G99/G97/G112/G97/G99/G105/G116/G105/G101/G115/G32/G111/G102/G32/G115/G117/G99/G104
/G111/G98/G106/G101/G99/G116/G115/G44/G32/G104/G111/G119/G32/G119/G111/G117/G108/G100/G32/G121/G111/G117/G32/G100/G111/G32/G105/G116/G63/G32/G87/G101/G32/G99/G97/G110/G110/G111/G116/G32/G99/G108/G97/G115/G115/G105/G102/G121
/G116/G104/G101/G115/G101/G32/G117/G110/G100/G101/G114/G32/G97/G110/G121/G32/G111/G102/G32/G116/G104/G101/G32/G115/G111/G108/G105/G100/G115/G32/G121/G111/G117/G32/G104/G97/G118/G101/G32/G97/G108/G114/G101/G97/G100/G121/G32/G115/G116/G117/G100/G105/G101/G100/G46
/G73/G110/G32/G116/G104/G105/G115/G32/G99/G104/G97/G112/G116/G101/G114/G44/G32/G121/G111/G117/G32/G119/G105/G108/G108/G32/G115/G101/G101/G32/G104/G111/G119/G32/G116/G111/G32/G102/G105/G110/G100/G32/G115/G117/G114/G102/G97/G99/G101/G32/G97/G114/G101/G97/G115/G32/G97/G110/G100/G32/G118/G111/G108/G117/G109/G101/G115/G32/G111/G102/G32/G115/G117/G99/G104
/G111/G98/G106/G101/G99/G116/G115/G46
/G49/G50/G46/G50 /G83/G117/G114/G102/G97/G99/G101/G32 /G65/G114/G101/G97/G32/G111/G102/G32/G97/G32/G67/G111/G109/G98/G105/G110/G97/G116/G105/G111/G110/G32/G111/G102/G32/G83/G111/G108/G105/G100/G115
/G76/G101/G116/G32/G117/G115/G32/G99/G111/G110/G115/G105/G100/G101/G114/G32/G116/G104/G101/G32/G99/G111/G110/G116/G97/G105/G110/G101/G114/G32/G115/G101/G101/G110/G32/G105/G110/G32/G70/G105/G103/G46/G32/G49/G50/G46/G50/G46/G32/G72/G111/G119/G32/G100/G111/G32/G119/G101/G32/G102/G105/G110/G100/G32/G116/G104/G101/G32/G115/G117/G114/G102/G97/G99/G101/G32/G97/G114/G101/G97/G32/G111/G102
/G115/G117/G99/G104/G32/G97/G32/G115/G111/G108/G105/G100/G63/G32/G78/G111/G119/G44/G32/G119/G104/G101/G110/G101/G118/G101/G114/G32/G119/G101/G32/G99/G111/G109/G101/G32/G97/G99/G114/G111/G115/G115/G32/G97/G32/G110/G101/G119/G32/G112/G114/G111/G98/G108/G101/G109/G44/G32/G119/G101/G32/G102/G105/G114/G115/G116/G32/G116/G114/G121/G32/G116/G111/G32/G115/G101/G101/G44/G32/G105/G102
/G119/G101/G32/G99/G97/G110/G32/G98/G114/G101/G97/G107/G32/G105/G116/G32/G100/G111/G119/G110/G32/G105/G110/G116/G111/G32/G115/G109/G97/G108/G108/G101/G114/G32/G112/G114/G111/G98/G108/G101/G109/G115/G44/G32/G119/G101/G32/G104/G97/G118/G101/G32/G101/G97/G114/G108/G105/G101/G114/G32/G115/G111/G108/G118/G101/G100/G46/G32/G87/G101/G32/G99/G97/G110/G32/G115/G101/G101/G32/G116/G104/G97/G116
/G116/G104/G105/G115/G32/G115/G111/G108/G105/G100/G32/G105/G115/G32/G109/G97/G100/G101/G32/G117/G112/G32/G111/G102/G32/G97/G32/G99/G121/G108/G105/G110/G100/G101/G114/G32/G119/G105/G116/G104/G32/G116/G119/G111/G32/G104/G101/G109/G105/G115/G112/G104/G101/G114/G101/G115/G32/G115/G116/G117/G99/G107/G32/G97/G116/G32/G101/G105/G116/G104/G101/G114/G32/G101/G110/G100/G46/G32/G73/G116/G32/G119/G111/G117/G108/G100
/G108/G111/G111/G107/G32/G108/G105/G107/G101/G32/G119/G104/G97/G116/G32/G119/G101/G32/G104/G97/G118/G101/G32/G105/G110/G32/G70/G105/G103/G46/G32/G49/G50/G46/G52/G44/G32/G97/G102/G116/G101/G114/G32/G119/G101/G32/G112/G117/G116/G32/G116/G104/G101/G32/G112/G105/G101/G99/G101/G115/G32/G97/G108/G108/G32/G116/G111/G103/G101/G116/G104/G101/G114/G46
/G70/G105/G103/G46/G32 /G49/G50/G46/G52
/G73/G102/G32/G119/G101/G32/G99/G111/G110/G115/G105/G100/G101/G114/G32/G116/G104/G101/G32/G115/G117/G114/G102/G97/G99/G101/G32/G111/G102/G32/G116/G104/G101/G32/G110/G101/G119/G108/G121/G32/G102/G111/G114/G109/G101/G100/G32/G111/G98/G106/G101/G99/G116/G44/G32/G119/G101/G32/G119/G111/G117/G108/G100/G32/G98/G101/G32/G97/G98/G108/G101/G32/G116/G111/G32/G115/G101/G101
/G111/G110/G108/G121/G32/G116/G104/G101/G32
/G99/G117/G114/G118/G101/G100/G32/G115/G117/G114/G102/G97/G99/G101/G115/G32/G111/G102/G32/G116/G104/G101/G32/G116/G119/G111/G32/G104/G101/G109/G105/G115/G112/G104/G101/G114/G101/G115/G32/G97/G110/G100/G32/G116/G104/G101/G32/G99/G117/G114/G118/G101/G100/G32/G115/G117/G114/G102/G97/G99/G101/G32/G111/G102/G32/G116/G104/G101/G32/G99/G121/G108/G105/G110/G100/G101/G114/G46
/G83/G111/G44/G32/G116/G104/G101/G32/G116/G111/G116/G97/G108/G32/G115/G117/G114/G102/G97/G99/G101/G32/G97/G114/G101/G97/G32/G111/G102/G32/G116/G104/G101/G32/G110/G101/G119/G32/G115/G111/G108/G105/G100/G32/G105/G115/G32/G116/G104/G101/G32/G115/G117/G109/G32/G111/G102/G32/G116/G104/G101/G32/G99/G117/G114/G118/G101/G100/G32/G115/G117/G114/G102/G97/G99/G101
/G97/G114/G101/G97/G115/G32/G111/G102/G32/G101/G97/G99/G104/G32/G111/G102/G32/G116/G104/G101/G32/G105/G110/G100/G105/G118/G105/G100/G117/G97/G108/G32/G112/G97/G114/G116/G115/G46/G32/G84/G104/G105/G115/G32/G103/G105/G118/G101/G115/G44
/G84/G83/G65/G32/G111/G102/G32/G110/G101/G119/G32/G115/G111/G108/G105/G100/G32/G61/G32/G67/G83/G65/G32/G111/G102/G32/G111/G110/G101/G32/G104/G101/G109/G105/G115/G112/G104/G101/G114/G101/G32/G43/G32/G67/G83/G65/G32/G111/G102/G32/G99/G121/G108/G105/G110/G100/G101/G114
/G32/G32/G32/G32/G32/G32/G32/G32/G32/G32/G32/G32/G32/G32/G32/G32/G32/G32/G32/G32/G32/G32/G32/G32/G32/G32/G32/G32/G32 /G43/G32/G67/G83/G65/G32/G111/G102/G32/G111/G116/G104/G101/G114/G32/G104/G101/G109/G105/G115/G112/G104/G101/G114/G101
/G119/G104/G101/G114/G101/G32/G84/G83/G65/G44/G32/G67/G83/G65/G32/G115/G116/G97/G110/G100/G32/G102/G111/G114/G32/G145/G84/G111/G116/G97/G108/G32/G83/G117/G114/G102/G97/G99/G101/G32/G65/G114/G101/G97/G146/G32/G97/G110/G100/G32/G145/G67/G117/G114/G118/G101/G100/G32/G83/G117/G114/G102/G97/G99/G101/G32/G65/G114/G101/G97/G146
/G114/G101/G115/G112/G101/G99/G116/G105/G118/G101/G108/G121/G46
/G76/G101/G116/G32/G117/G115/G32/G110/G111/G119/G32/G99/G111/G110/G115/G105/G100/G101/G114/G32/G97/G110/G111/G116/G104/G101/G114/G32/G115/G105/G116/G117/G97/G116/G105/G111/G110/G46/G32/G83/G117/G112/G112/G111/G115/G101/G32/G119/G101/G32/G97/G114/G101/G32/G109/G97/G107/G105/G110/G103/G32/G97/G32/G116/G111/G121/G32/G98/G121/G32/G112/G117/G116/G116/G105/G110/G103
/G116/G111/G103/G101/G116/G104/G101/G114/G32/G97/G32/G104/G101/G109/G105/G115/G112/G104/G101/G114/G101/G32/G97/G110/G100/G32/G97/G32/G99/G111/G110/G101/G46/G32/G76/G101/G116/G32/G117/G115/G32/G115/G101/G101/G32/G116/G104/G101/G32/G115/G116/G101/G112/G115/G32/G116/G104/G97/G116/G32/G119/G101/G32/G119/G111/G117/G108/G100/G32/G98/G101/G32/G103/G111/G105/G110/G103
/G116/G104/G114/G111/G117/G103/G104/G46
/G70/G105/G103/G46/G32 /G49/G50/G46/G51
```

### 3. pypdfium2 (Current)
```text
 	
$
 %	



&'
#$
(
	 

	
)

	

	


*

		
	 		
 


	
	



	

 
!      

   	  

  
%	
#+	

	
 	

!
 
		   
    	  
%
 	
			
,



-

	
#. 	




			 	
	 +

	

	



!	
		
 

/
		
 	
!
	%		
	 
 	

*    	

   	



 
	)

 
)*$	
0'*$
1'*$	

 1'*$

 )*$ '*$   2)	 *$3  2'  *$3

 	
,


*


  
    ,     	  


 
```

---

## Sample 28 [CHUNK_ID: chk_a8ef9339fd1d7f95]
**Document:** STD-10/Std-10_Maths_EnglishMedium.pdf | **Page:** 252

### 1. PyMuPDF (fitz)
```text

		
;D
	
!




	!	

1)(%

0
'	!()("

)	./
-
%#
	P

	%#
"!


P;P8P8

	


		P;P8P8
!P



	%#



		
C
!P;
		
/85H0
	
%#!




	

-
P;
	
%#












L!	P:
	%#!
 



	85H




	

P:
		
		
	
P;
"

		
P8P8
!P:EP;




!






P;

P	!
!!
+
		
			


	
P;	
 
	

%#
```

### 2. pypdf (Native)
```text
/G80/G82/G79/G79/G70/G83/G32/G73/G78/G32/G77/G65 /G84/G72/G69/G77/G65 /G84/G73/G67/G83 /G50/G51/G55
/G82/G101/G109/G97/G114/G107/G32/G58/G32/G84/G104/G101/G32/G101/G120/G97/G109/G112/G108/G101/G32/G111/G102/G32/G116/G104/G101/G32/G112/G114/G111/G111/G102/G32/G97/G98/G111/G118/G101/G32/G115/G104/G111/G119/G115/G32/G121/G111/G117/G44/G32/G121/G101/G116/G32/G97/G103/G97/G105/G110/G44/G32/G116/G104/G97/G116/G32/G116/G104/G101/G114/G101/G32/G99/G97/G110/G32/G98/G101
/G115/G101/G118/G101/G114/G97/G108/G32/G119/G97/G121/G115/G32/G111/G102/G32/G112/G114/G111/G118/G105/G110/G103/G32/G97/G32/G114/G101/G115/G117/G108/G116/G46
/G84/G104/G101/G111/G114
/G101/G109/G32/G65/G49/G46/G50/G32/G58/G32/G79/G117/G116/G32/G111/G102/G32/G97/G108/G108/G32/G116/G104/G101/G32/G108/G105/G110/G101/G32/G115/G101/G103/G109/G101/G110/G116/G115/G44/G32/G100/G114/G97/G119/G110/G32/G102/G114/G111/G109/G32/G97/G32/G112/G111/G105/G110/G116/G32/G116/G111/G32/G112/G111/G105/G110/G116/G115/G32/G111/G102/G32/G97
/G108/G105/G110/G101/G32
/G110/G111/G116/G32/G112/G97/G115/G115/G105/G110/G103/G32/G116/G104/G114/G111/G117/G103/G104/G32/G116/G104/G101/G32/G112/G111/G105/G110/G116/G44/G32/G116/G104/G101/G32/G115/G109/G97/G108/G108/G101/G115/G116/G32/G105/G115/G32/G116/G104/G101/G32/G112/G101/G114/G112/G101/G110/G100/G105/G99/G117/G108/G97/G114/G32/G116/G111/G32/G116/G104/G101/G32/G108/G105/G110/G101/G46
/G80/G114/G111/G111/G102/G32/G58
/G70/G105/G103/G46/G32/G65
/G49/G46/G53
/G83/G116/G97/G116/G101/G109/G101/G110/G116/G115/G65/G110/G97/G108/G121/G115/G105/G115/G47/G67/G111/G109/G109/G101/G110/G116
/G76/G101/G116/G32/G88/G89/G32
/G98/G101/G32/G116/G104/G101/G32/G103/G105/G118/G101/G110/G32/G108/G105/G110/G101/G44/G32/G80/G32/G97/G32/G112/G111/G105/G110/G116/G32/G110/G111/G116/G32/G108/G121/G105/G110/G103/G32/G111/G110/G32/G88/G89 /G83/G105/G110/G99/G101/G32/G119/G101/G32/G104/G97/G118/G101/G32/G116/G111/G32/G112/G114/G111/G118/G101/G32/G116/G104/G97/G116
/G97/G110/G100/G32/G80/G77/G44/G32/G80/G65/G49/G44/G32/G80/G65/G50/G44/G32/G46/G32/G46/G32/G46/G32/G101/G116/G99/G46/G44/G32/G98/G101/G32/G116/G104/G101/G32/G108/G105/G110/G101/G32/G115/G101/G103/G109/G101/G110/G116/G115 /G111/G117/G116/G32/G111/G102/G32/G97/G108/G108/G32/G80/G77/G44/G32/G80/G65/G49/G44/G32/G80/G65/G50/G44/G32/G46/G32/G46/G32/G46
/G100/G114/G97/G119/G110/G32/G102/G114/G111/G109/G32/G80/G32/G116/G111/G32/G116/G104/G101/G32/G112/G111/G105/G110/G116/G115/G32/G111/G102/G32/G116/G104/G101/G32/G108/G105/G110/G101/G32/G88/G89/G44/G32/G111/G117/G116/G32/G111/G102 /G101/G116/G99/G46/G44/G32/G116/G104/G101/G32/G115/G109/G97/G108/G108/G101/G115/G116/G32/G105/G115/G32/G112/G101/G114/G112/G101/G110/G100/G105/G45
/G119/G104/G105/G99/G104/G32/G80/G77/G32/G105/G115/G32/G116/G104/G101/G32/G115/G109/G97/G108/G108/G101/G115/G116/G32/G40/G115/G101/G101/G32/G70/G105/G103/G46/G32/G65/G49/G46/G53/G41/G46 /G99/G117/G108/G97/G114/G32/G116/G111/G32/G88/G89/G44/G32/G119/G101/G32/G115/G116/G97/G114/G116/G32/G98/G121
/G116/G97/G107/G105/G110/G103/G32/G116/G104/G101/G115/G101/G32/G108/G105/G110/G101/G32/G115/G101/G103/G109/G101/G110/G116/G115/G46
/G76/G101/G116/G32/G80/G77/G32/G98/G101/G32/G110/G111/G116/G32/G112/G101/G114/G112/G101/G110/G100/G105/G99/G117/G108/G97/G114/G32/G116/G111/G32/G88/G89 /G84/G104/G105/G115/G32/G105/G115/G32/G116/G104/G101/G32/G110/G101/G103/G97/G116/G105/G111/G110/G32/G111/G102/G32/G116/G104/G101
/G115/G116/G97/G116/G101/G109/G101/G110/G116/G32/G116/G111/G32/G98/G101/G32/G112/G114/G111/G118/G101/G100/G32/G98/G121
/G99/G111/G110/G116/G114/G97/G100/G105/G99/G116/G105/G111/G110/G46
/G68/G114/G97/G119/G32/G97/G32/G112/G101/G114/G112/G101/G110/G100/G105/G99/G117/G108/G97/G114/G32/G80/G78/G32/G111/G110/G32/G116/G104/G101/G32/G108/G105/G110/G101/G32/G88/G89/G44/G32/G115/G104/G111/G119/G110 /G87/G101/G32/G111/G102/G116/G101/G110/G32/G110/G101/G101/G100
/G98/G121/G32/G100/G111/G116/G116/G101/G100/G32/G108/G105/G110/G101/G115/G32/G105/G110/G32/G70/G105/G103/G46/G32/G65/G49/G46/G53/G46 /G99/G111/G110/G115/G116/G114/G117/G99/G116/G105/G111/G110/G115/G32/G116/G111/G32/G112/G114/G111/G118/G101/G32/G111/G117/G114
/G114/G101/G115/G117/G108/G116/G115/G46
/G80/G78/G32/G105/G115/G32/G116/G104/G101/G32/G115/G109/G97/G108/G108/G101/G115/G116/G32/G111/G102/G32/G97/G108/G108/G32/G116/G104/G101/G32/G108/G105/G110/G101/G32/G115/G101/G103/G109/G101/G110/G116/G115/G32/G80/G77/G44 /G83/G105/G100/G101/G32/G111/G102/G32/G114/G105/G103/G104/G116/G32/G116/G114/G105/G97/G110/G103/G108/G101/G32/G105/G115/G32/G108/G101/G115/G115
/G80/G65/G49/G44/G32/G80/G65/G50/G44/G32/G46/G32/G46/G32/G46/G32/G101/G116/G99/G46/G44/G32/G119/G104/G105/G99/G104/G32/G109/G101/G97/G110/G115/G32/G80/G78/G32/G60/G32/G80/G77/G46 /G116/G104/G97/G110/G32/G116/G104/G101/G32/G104/G121/G112/G111/G116/G101/G110/G117/G115/G101/G32/G97/G110/G100
/G107/G110/G111/G119/G110/G32/G112/G114/G111/G112/G101/G114/G116/G121/G32/G111/G102/G32/G110/G117/G109/G98/G101/G114/G115/G46
/G84/G104/G105/G115/G32/G99/G111/G110/G116/G114/G97/G100/G105/G99/G116/G115/G32/G111/G117/G114/G32/G104/G121/G112/G111/G116/G104/G101/G115/G105/G115/G32/G116/G104/G97/G116/G32/G80/G77/G32/G105/G115/G32/G116/G104/G101 /G80/G114/G101/G99/G105/G115/G101/G108/G121/G32/G119/G104/G97/G116/G32/G119/G101/G32/G119/G97/G110/G116/G33
/G115/G109/G97/G108/G108/G101/G115/G116/G32/G111/G102/G32/G97/G108/G108/G32/G115/G117/G99/G104/G32/G108/G105/G110/G101/G32/G115/G101/G103/G109/G101/G110/G116/G115/G46
/G84/G104/G101/G114/G101/G102/G111/G114/G101/G44/G32/G116/G104/G101/G32/G108/G105/G110/G101/G32/G115/G101/G103/G109/G101/G110/G116/G32/G80/G77/G32/G105/G115/G32/G112/G101/G114/G112/G101/G110/G100/G105/G99/G117/G108/G97/G114 /G87/G101/G32/G114/G101/G97/G99/G104/G32/G116/G104/G101/G32/G99/G111/G110/G99/G108/G117/G115/G105/G111/G110/G46
/G116/G111/G32/G88/G89/G46
```

### 3. pypdfium2 (Current)
```text

	 	 ;D
 	
!




	!	

1)(  %         
     
0
'	!()("
 )	./
-
%#
	P

	%# "!



P;P8
P8

	
 
		P;P8P8
!P



	%#
 

		
C
!P;
		
/85H0 	
%#!




	

-
P;
	
%# 











L!	P:
	%#! 



	85H 



	

P:
		
		
	
P; "

		
P8
P8
!P:EP; 



!






P;
 P	!
!!
+
		
			


	
P;	 
	

%#
```

---

## Sample 29 [CHUNK_ID: chk_746ed687d1f49761]
**Document:** STD-10/Std-10_Science_English Medium.pdf | **Page:** 76

### 1. PyMuPDF (fitz)
```text
Carbon and its Compounds
63
Organic compounds
The two characteristic features seen in carbon, that is, tetravalency and catenation, put
together give rise to a large number of compounds. Many have the same non-carbon
atom or group of atoms attached to different carbon chains. These compounds were
initially extracted from natural substances and it was thought that these carbon
compounds or organic compounds could only be formed within a living system. That is,
it was postulated that a ‘vital force’ was necessary for their synthesis. Friedrich Wöhler
disproved this in 1828 by preparing urea from ammonium cyanate. But carbon
compounds, except for carbides, oxides of carbon, carbonate and hydrogencarbonate
salts continue to be studied under organic chemistry.
4.2.1 Saturated and Unsaturated Carbon Compounds
4.2.1 Saturated and Unsaturated Carbon Compounds
4.2.1 Saturated and Unsaturated Carbon Compounds
4.2.1 Saturated and Unsaturated Carbon Compounds
4.2.1 Saturated and Unsaturated Carbon Compounds
We have already seen the structure of methane. Another compound
formed between carbon and hydrogen is ethane with a formula of C2H6.
In order to arrive at the structure of simple carbon
compounds, the first step is to link the carbon atoms
together with a single bond (Fig. 4.6a) and then use the
hydrogen atoms to satisfy the remaining valencies of carbon
(Fig. 4.6b). For example, the structure of ethane is arrived
in the following steps –
C—C
Step 1
Figure 4.6 
Figure 4.6 
Figure 4.6 
Figure 4.6 
Figure 4.6 (a) Carbon atoms linked together with a single bond
Three valencies of each carbon atom remain unsatisfied,
so each is bonded to three hydrogen atoms giving:
Step 2
Figure 4.6 
Figure 4.6 
Figure 4.6 
Figure 4.6 
Figure 4.6 (b) Each carbon atom bonded to three hydrogen atoms
The electron dot structure of ethane is shown in Fig. 4.6(c).
Can you draw the structure of propane, which has the molecular
formula C3H8 in a similar manner? You will see that the valencies of all
the atoms are satisfied by single bonds between them. Such carbon
compounds are called saturated compounds. These compounds are
normally not very reactive.
However, another compound of carbon and hydrogen has the formula
C2H4 and is called ethene. How can this molecule be depicted? We follow
the same step-wise approach as above.
Carbon-carbon atoms linked together with a single bond (Step 1).
We see that one valency per carbon atom remains unsatisfied
(Step 2). This can be satisfied only if there is a double bond between the
two carbons (Step 3).
Figure 4.6
Figure 4.6
Figure 4.6
Figure 4.6
Figure 4.6
(c) Electron dot structure of
ethane
More to Know!
Step 2
Step 3
C—C        Step 1
```

### 2. pypdf (Native)
```text
Carbon and its Compounds 63
Organic compounds
The two characteristic features seen in carbon, that is, tetravalency and catenation, put
together give rise to a large number of compounds. Many have the same non-carbon
atom or group of atoms attached to different carbon chains. These compounds were
initially extracted from natural substances and it was thought that these carbon
compounds or organic compounds could only be formed within a living system. That is,
it was postulated that a ‘vital force’ was necessary for their synthesis. Friedrich Wöhler
disproved this in 1828 by preparing urea from ammonium cyanate. But carbon
compounds, except for carbides, oxides of carbon, carbonate and hydrogencarbonate
salts continue to be studied under organic chemistry.
4.2.1 Saturated and Unsaturated Carbon Compounds4.2.1 Saturated and Unsaturated Carbon Compounds4.2.1 Saturated and Unsaturated Carbon Compounds4.2.1 Saturated and Unsaturated Carbon Compounds4.2.1 Saturated and Unsaturated Carbon Compounds
We have alr
eady seen the structure of methane. Another compound
formed between carbon and hydrogen is ethane with a formula of C2H6.
In order to arrive at the structure of simple carbon
compounds, the first step is to link the carbon atoms
together with a single bond (Fig. 4.6a) and then use the
hydrogen atoms to satisfy the remaining valencies of carbon
(Fig. 4.6b). For example, the structure of ethane is arrived
in the following steps –
C—C Step 1
Figure 4.6 Figure 4.6 Figure 4.6 Figure 4.6 Figure 4.6 (a) Carbon atoms linked together with a single bond
Three valencies of each carbon atom remain unsatisfied,
so each is bonded to three hydrogen atoms giving:
Step 2
Figure 4.6 Figure 4.6 Figure 4.6 Figure 4.6 Figure 4.6 (b)     Each carbon atom bonded to three hydrogen atoms
The electron dot structure of ethane is shown in Fig. 4.6(c).
Can you draw the structure of propane, which has the molecular
formula C3H8 in a similar manner? You will see that the valencies of all
the atoms are satisfied by single bonds between them. Such carbon
compounds are called saturated compounds. These compounds are
normally not very reactive.
However, another compound of carbon and hydrogen has the formula
C2H4 and is called ethene. How can this molecule be depicted? We follow
the same step-wise approach as above.
Carbon-carbon atoms linked together with a single bond (Step 1).
We see that one valency per carbon atom r emains unsatisfied
(Step 2). This can be satisfied only if there is a double bond between the
two carbons (Step 3).
Figure 4.6Figure 4.6Figure 4.6Figure 4.6Figure 4.6
(c) 
    Electron dot structure of
ethane
More to Know!
Step 2
Step 3
C—C        Step 1
```

### 3. pypdfium2 (Current)
```text
Carbon and its Compounds 63
Organic compounds
The two characteristic features seen in carbon, that is, tetravalency and catenation, put
together give rise to a large number of compounds. Many have the same non-carbon
atom or group of atoms attached to different carbon chains. These compounds were
initially extracted from natural substances and it was thought that these carbon
compounds or organic compounds could only be formed within a living system. That is,
it was postulated that a ‘vital force’ was necessary for their synthesis. Friedrich Wöhler
disproved this in 1828 by preparing urea from ammonium cyanate. But carbon
compounds, except for carbides, oxides of carbon, carbonate and hydrogencarbonate
salts continue to be studied under organic chemistry.
4.2.1 Saturated and Unsaturated Carbon Compounds
We have already seen the structure of methane. Another compound
formed between carbon and hydrogen is ethane with a formula of C2H6.
In order to arrive at the structure of simple carbon
compounds, the first step is to link the carbon atoms
together with a single bond (Fig. 4.6a) and then use the
hydrogen atoms to satisfy the remaining valencies of carbon
(Fig. 4.6b). For example, the structure of ethane is arrived
in the following steps –
C—C Step 1
Figure 4.6 (a) Carbon atoms linked together with a single bond
Three valencies of each carbon atom remain unsatisfied,
so each is bonded to three hydrogen atoms giving:
Step 2
Figure 4.6 (b) Each carbon atom bonded to three hydrogen atoms
The electron dot structure of ethane is shown in Fig. 4.6(c).
Can you draw the structure of propane, which has the molecular
formula C3H8 in a similar manner? You will see that the valencies of all
the atoms are satisfied by single bonds between them. Such carbon
compounds are called saturated compounds. These compounds are
normally not very reactive.
However, another compound of carbon and hydrogen has the formula
C2H4 and is called ethene. How can this molecule be depicted? We follow
the same step-wise approach as above.
Carbon-carbon atoms linked together with a single bond (Step 1).
We see that one valency per carbon atom remains unsatisfied
(Step 2). This can be satisfied only if there is a double bond between the
two carbons (Step 3).
Figure 4.6
(c) Electron dot structure of
ethane
More to Know!
Step 2
Step 3
C—C Step 1
```

---

## Sample 30 [CHUNK_ID: chk_f77224f721cef554]
**Document:** STD-10/Std-10_Science_English Medium.pdf | **Page:** 102

### 1. PyMuPDF (fitz)
```text
Life Processes
89
cells, or away from them and out into the air. The direction of diffusion
depends upon the environmental conditions and the requirements of
the plant. At night, when there is no photosynthesis occurring, CO2
elimination is the major exchange activity going on. During the day,
CO2 generated during respiration is used up for photosynthesis, hence
there is no CO2 release. Instead, oxygen release is the major event at
this time.
Animals have evolved different organs for the uptake of oxygen
from the environment and for getting rid of the carbon dioxide
produced. Terrestrial animals can breathe the oxygen in the
atmosphere, but animals that live in water need to use the oxygen
dissolved in water.
Activity 5.6
Activity 5.6
Activity 5.6
Activity 5.6
Activity 5.6
n
Observe fish in an aquarium. They open and close their mouths
and the gill-slits (or the operculum which covers the gill-slits)
behind their eyes also open and close. Are the timings of the
opening and closing of the mouth and gill-slits coordinated in some
manner?
n
Count the number of times the fish opens and closes its mouth in
a minute.
n
Compare this to the number of times you breathe in and out in a
minute.
Since the amount of dissolved oxygen is fairly low compared
to the amount of oxygen in the air, the rate of breathing in aquatic
organisms is much faster than that seen in terrestrial organisms.
Fishes take in water through their mouths and force it past the
gills where the dissolved oxygen is taken up by blood.
Terrestrial organisms use the oxygen in the atmosphere for
respiration. This oxygen is absorbed by different organs in
different animals. All these organs have a structure that increases
the surface area which is in contact with the oxygen-rich
atmosphere. Since the exchange of oxygen and carbon dioxide
has to take place across this surface, this surface is very fine
and delicate. In order to protect this surface, it is usually placed
within the body, so there have to be passages that will take air
to this area. In addition, there is a mechanism for moving the air
in and out of this area where the oxygen is absorbed.
In human beings (Fig. 5.9), air is taken into the body through
the nostrils. The air passing through the nostrils is filtered by
fine hairs that line the passage. The passage is also lined with
mucus which helps in this process. From here, the air passes
through the throat and into the lungs. Rings of cartilage are
present in the throat. These ensure that the air-passage does
not collapse.
Using tobacco directly or
any product of tobacco in
the form of cigar, cigarettes,
bidis, hookah, gutkha, etc.,
is harmful. Use of tobacco
most commonly affects the
tongue, lungs, heart and
liver. Smokeless tobacco is
also a major risk factor for
heart attacks, strokes,
pulmonary diseases and
several forms of cancers.
There is a high incidence of
oral cancer in India due to
the chewing of tobacco in
the form of gutkha. Stay
healthy; just say NO to
tobacco and its products!
More to Know!
```

### 2. pypdf (Native)
```text
Life Processes 89
cells, or away from them and out into the air. The direction of diffusion
depends upon the environmental conditions and the requirements of
the plant. At night, when there is no photosynthesis occurring, CO 2
elimination is the major exchange activity going on. During the day,
CO2 generated during respiration is used up for photosynthesis, hence
there is no CO2 release. Instead, oxygen release is the major event at
this time.
Animals have evolved different organs for the uptake of oxygen
from the environment and for getting rid of the carbon dioxide
produced. Terrestrial animals can breathe the oxygen in the
atmosphere, but animals that live in water need to use the oxygen
dissolved in water.
Activity 5.6Activity 5.6Activity 5.6Activity 5.6Activity 5.6
/square6Observe fish in an aquarium. They open and close their mouths
and the gill-slits (or the operculum which covers the gill-slits)
behind their eyes also open and close. Are the timings of the
opening and closing of the mouth and gill-slits coordinated in some
manner?
/square6Count the number of times the fish opens and closes its mouth in
a minute.
/square6Compare this to the number of times you breathe in and out in a
minute.
Since the amount of dissolved oxygen is fairly low compared
to the amount of oxygen in the air, the rate of breathing in aquatic
organisms is much faster than that seen in terrestrial organisms.
Fishes take in water through their mouths and force it past the
gills where the dissolved oxygen is taken up by blood.
Terrestrial organisms use the oxygen in the atmosphere for
respiration. This oxygen is absorbed by different organs in
different animals. All these organs have a structure that increases
the surface area which is in contact with the oxygen-rich
atmosphere. Since the exchange of oxygen and carbon dioxide
has to take place across this surface, this surface is very fine
and delicate. In order to protect this surface, it is usually placed
within the body, so there have to be passages that will take air
to this area. In addition, there is a mechanism for moving the air
in and out of this area where the oxygen is absorbed.
In human beings (Fig. 5.9), air is taken into the body through
the nostrils. The air passing through the nostrils is filtered by
fine hairs that line the passage. The passage is also lined with
mucus which helps in this process. From here, the air passes
through the throat and into the lungs. Rings of cartilage are
present in the throat. These ensure that the air-passage does
not collapse.
Using tobacco directly or
any product of tobacco in
the form of cigar, cigarettes,
bidis, hookah, gutkha, etc.,
is harmful. Use of tobacco
most commonly affects the
tongue, lungs, heart and
liver. Smokeless tobacco is
also a major risk factor for
heart attacks, strokes,
pulmonary diseases and
several forms of cancers.
There is a high incidence of
oral cancer in India due to
the chewing of tobacco in
the form of gutkha. Stay
healthy; just say NO to
tobacco and its products!
More to Know!
```

### 3. pypdfium2 (Current)
```text
Life Processes 89
cells, or away from them and out into the air. The direction of diffusion
depends upon the environmental conditions and the requirements of
the plant. At night, when there is no photosynthesis occurring, CO2
elimination is the major exchange activity going on. During the day,
CO2 generated during respiration is used up for photosynthesis, hence
there is no CO2 release. Instead, oxygen release is the major event at
this time.
Animals have evolved different organs for the uptake of oxygen
from the environment and for getting rid of the carbon dioxide
produced. Terrestrial animals can breathe the oxygen in the
atmosphere, but animals that live in water need to use the oxygen
dissolved in water.
Activity 5.6
n Observe fish in an aquarium. They open and close their mouths
and the gill-slits (or the operculum which covers the gill-slits)
behind their eyes also open and close. Are the timings of the
opening and closing of the mouth and gill-slits coordinated in some
manner?
n Count the number of times the fish opens and closes its mouth in
a minute.
n Compare this to the number of times you breathe in and out in a
minute.
Since the amount of dissolved oxygen is fairly low compared
to the amount of oxygen in the air, the rate of breathing in aquatic
organisms is much faster than that seen in terrestrial organisms.
Fishes take in water through their mouths and force it past the
gills where the dissolved oxygen is taken up by blood.
Terrestrial organisms use the oxygen in the atmosphere for
respiration. This oxygen is absorbed by different organs in
different animals. All these organs have a structure that increases
the surface area which is in contact with the oxygen-rich
atmosphere. Since the exchange of oxygen and carbon dioxide
has to take place across this surface, this surface is very fine
and delicate. In order to protect this surface, it is usually placed
within the body, so there have to be passages that will take air
to this area. In addition, there is a mechanism for moving the air
in and out of this area where the oxygen is absorbed.
In human beings (Fig. 5.9), air is taken into the body through
the nostrils. The air passing through the nostrils is filtered by
fine hairs that line the passage. The passage is also lined with
mucus which helps in this process. From here, the air passes
through the throat and into the lungs. Rings of cartilage are
present in the throat. These ensure that the air-passage does
not collapse.
Using tobacco directly or
any product of tobacco in
the form of cigar, cigarettes,
bidis, hookah, gutkha, etc.,
is harmful. Use of tobacco
most commonly affects the
tongue, lungs, heart and
liver. Smokeless tobacco is
also a major risk factor for
heart attacks, strokes,
pulmonary diseases and
several forms of cancers.
There is a high incidence of
oral cancer in India due to
the chewing of tobacco in
the form of gutkha. Stay
healthy; just say NO to
tobacco and its products!
More to Know!
```

---
