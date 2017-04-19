1. 根据每一种攻击设计攻击向量（找出所有最小元素，加以合适的组合；最小元素分等级）
2. 最小元素优先检测法，找出最小元素
3. 二分法确定ban元素
4. 扩展ban元素，找出正则


不可能把所有waf规则试探出来，只能用少数探测去猜正则
关键字如何分等级

特殊字符：!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~
特殊空格字符：%20%09%0a%0b%0c%0d%a0%00
注释符：-- // /**/ /*!50000*/
关键字：or union select as xor like in not and binary between isnull from all where group by having limit into outfile procedure
sql函数：round() pi() version() ascii() load_file() hex() ord() concat() conv() char() unhex()
aes_encrypt() des_encrypt() floor() ceil() pow() substr() substring() mid() lpad() rpad() left()
reverse() right() trim() insert() locate() position() instr() substring_index() strcmp()
length() password() md5() sha() group_concat() analyse()

sql关键字+组词造句
sql函数
sql常用库名、表名、字段名：
库名：information_schema
表名：tables columns sysobjects syscolumns admin password sysuser system
字段名：table_name column_name
 
 fuzz方法，元素之间插入不同种类的元素：
 1. 一般字符串
 2. 数字字符串
 3. 替换空格
 4. 特殊字符
 
 ' or 1=1#--/**///
 and 1=1 union select substr("123",1,1) 
 select 1,table_name from information_schema.columns where ascii(97)<>'A'
 
检查句子中间是否存在被ban的字符串并删去
被ban的字符串要改为大小写重试、中间增加fuzz重试

剩下任务：
7. 删除已有模式
8. 多线程
3. 模式探测
4. 模式归类并输出

解决任务：
1. 设计payload
2. 关键字分裂
5. payload归类添加err
6. bound成功时要删去