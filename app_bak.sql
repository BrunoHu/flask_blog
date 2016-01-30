PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE user (
	id INTEGER NOT NULL, 
	nickname VARCHAR(64), 
	password VARCHAR(120), 
	about_me VARCHAR(140), 
	last_seen DATETIME, 
	PRIMARY KEY (id)
);
INSERT INTO "user" VALUES(1,'hbc','12345','呵呵哒','2016-01-18 15:04:38.096895');
INSERT INTO "user" VALUES(2,'little','12345',NULL,NULL);
INSERT INTO "user" VALUES(3,'bighbc','12345',NULL,NULL);
INSERT INTO "user" VALUES(4,'hahahbc','12345',NULL,NULL);
INSERT INTO "user" VALUES(5,'hehehbc','12345',NULL,NULL);
INSERT INTO "user" VALUES(6,'mamahbc','12345',NULL,'2016-01-07 13:05:46.659106');
INSERT INTO "user" VALUES(7,'hulala','12345',NULL,'2016-01-07 18:56:56.735598');
INSERT INTO "user" VALUES(8,'h','12345',NULL,'2016-01-12 09:28:08.650546');
INSERT INTO "user" VALUES(9,'','12345',NULL,'2016-01-07 19:10:46.763364');
CREATE TABLE post (
	id INTEGER NOT NULL, 
	body VARCHAR(140), 
	timestamp DATETIME, 
	user_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES user (id)
);
INSERT INTO "post" VALUES(1,'test search','2016-01-07 13:01:25.879201',6);
INSERT INTO "post" VALUES(2,'try to sleep','2016-01-07 13:01:33.107045',6);
INSERT INTO "post" VALUES(3,'search test','2016-01-07 13:01:44.149595',6);
INSERT INTO "post" VALUES(4,'search1','2016-01-07 13:01:51.256237',6);
INSERT INTO "post" VALUES(5,'unique test','2016-01-07 13:02:03.473268',6);
INSERT INTO "post" VALUES(6,'','2016-01-07 13:06:51.781658',1);
INSERT INTO "post" VALUES(7,'uuu','2016-01-07 13:06:58.155376',1);
INSERT INTO "post" VALUES(8,'dadasawdw','2016-01-07 14:52:42.803851',1);
INSERT INTO "post" VALUES(9,'gewgwegw','2016-01-07 14:53:02.483131',1);
INSERT INTO "post" VALUES(10,'haha','2016-01-07 14:55:32.722457',1);
INSERT INTO "post" VALUES(11,'','2016-01-07 15:08:59.261903',1);
INSERT INTO "post" VALUES(12,'','2016-01-07 15:14:13.430139',1);
INSERT INTO "post" VALUES(13,'还不错','2016-01-07 15:14:46.276318',1);
INSERT INTO "post" VALUES(14,'gwgwgwe','2016-01-11 17:26:40.742341',8);
INSERT INTO "post" VALUES(15,'dssfsf','2016-01-11 17:26:43.090777',8);
INSERT INTO "post" VALUES(16,'afassc','2016-01-11 17:26:45.485718',8);
INSERT INTO "post" VALUES(17,'qqwfsc','2016-01-11 17:26:48.158088',8);
INSERT INTO "post" VALUES(18,'test api','2016-01-12 08:55:06.383043',8);
INSERT INTO "post" VALUES(19,'哈哈哈','2016-01-12 16:19:03.524436',1);
INSERT INTO "post" VALUES(20,'试试','2016-01-17 09:45:28.316220',1);
INSERT INTO "post" VALUES(21,'发表了一篇文章:title','2016-01-17 12:16:29.093783',1);
INSERT INTO "post" VALUES(22,'发表了一篇文章:title','2016-01-17 13:00:29.758227',1);
INSERT INTO "post" VALUES(23,'发表了一篇文章:测试标题','2016-01-17 13:20:58.385152',1);
INSERT INTO "post" VALUES(24,'发表了一篇文章<a href=''''/essay/4''''>u''\u5475\u5475''</a>','2016-01-17 13:31:55.371997',1);
INSERT INTO "post" VALUES(25,'发表了一篇文章<a href=''''/essay/5''''>u''hehe''</a>','2016-01-17 13:33:19.959323',1);
INSERT INTO "post" VALUES(26,'发表了一篇文章<a href=''''/essay/7''''>u''hehe''</a>','2016-01-17 13:38:02.668353',1);
INSERT INTO "post" VALUES(27,'发表了一篇文章<a href=''''/essay/title/%3Cinput%20id%3D%22title%22%20name%3D%22title%22%20type%3D%22text%22%20value%3D%22hehe%22%3E''''><wtforms.fields.core.StringField object at 0x7f578f744110></a>','2016-01-17 13:42:23.666786',1);
INSERT INTO "post" VALUES(28,'发表了一篇文章<a href=''''/essay/title/hehe''''>u''hehe''</a>','2016-01-17 13:42:53.618638',1);
INSERT INTO "post" VALUES(29,'发表了一篇文章<a href=''/essay/title/haha''>haha</a>','2016-01-17 13:44:53.056607',1);
INSERT INTO "post" VALUES(30,'发表了一篇文章---<a href=''/essay/title/ceshi''>ceshi</a>','2016-01-17 13:56:12.783701',1);
CREATE TABLE followers (
	follower_id INTEGER, 
	followed_id INTEGER, 
	FOREIGN KEY(follower_id) REFERENCES user (id), 
	FOREIGN KEY(followed_id) REFERENCES user (id)
);
INSERT INTO "followers" VALUES(1,1);
INSERT INTO "followers" VALUES(2,2);
INSERT INTO "followers" VALUES(3,3);
INSERT INTO "followers" VALUES(4,4);
INSERT INTO "followers" VALUES(5,5);
INSERT INTO "followers" VALUES(6,6);
INSERT INTO "followers" VALUES(6,1);
INSERT INTO "followers" VALUES(6,3);
INSERT INTO "followers" VALUES(1,5);
INSERT INTO "followers" VALUES(7,7);
INSERT INTO "followers" VALUES(8,8);
INSERT INTO "followers" VALUES(9,9);
INSERT INTO "followers" VALUES(1,2);
INSERT INTO "followers" VALUES(1,8);
INSERT INTO "followers" VALUES(8,5);
INSERT INTO "followers" VALUES(1,3);
INSERT INTO "followers" VALUES(1,7);
CREATE TABLE migrate_version (
	repository_id VARCHAR(250) NOT NULL, 
	repository_path TEXT, 
	version INTEGER, 
	PRIMARY KEY (repository_id)
);
INSERT INTO "migrate_version" VALUES('database repository','/home/arnold-hu/new_blog/db_repository',2);
CREATE TABLE essay (
	id INTEGER NOT NULL, 
	title VARCHAR, 
	body TEXT, 
	timestamp DATETIME, 
	user_id INTEGER, body_html TEXT, 
	PRIMARY KEY (id)
);
INSERT INTO "essay" VALUES(1,'title','# body ','2016-01-17 12:16:28.871896',1,NULL);
INSERT INTO "essay" VALUES(2,'title','# title','2016-01-17 13:00:29.547114',1,'<h1>title</h1>');
INSERT INTO "essay" VALUES(3,'测试标题','# 测试标题
## 2号大小
### 3好大小
> 测试引用

`测试代码行`

```
测试
代码快
```

1.  1号
2.  2号
5. 3号','2016-01-17 13:20:58.119540',1,'<h1>测试标题</h1>
<h2>2号大小</h2>
<h3>3好大小</h3>

<p>测试引用</p>

<p><code>测试代码行</code></p>
<p><code>测试
代码快</code></p>
<ol>
<li>1号</li>
<li>2号</li>
<li>3号</li>
</ol>');
INSERT INTO "essay" VALUES(4,'呵呵','> 哈哈','2016-01-17 13:31:55.371997',1,'
<p>哈哈</p>
');
INSERT INTO "essay" VALUES(5,'hehe','haha','2016-01-17 13:33:19.959323',1,'<p>haha</p>');
INSERT INTO "essay" VALUES(6,'hehe','haha','2016-01-17 13:37:39.087624',1,'<p>haha</p>');
INSERT INTO "essay" VALUES(7,'hehe','haha','2016-01-17 13:38:02.668353',1,'<p>haha</p>');
INSERT INTO "essay" VALUES(8,'hehe','haha','2016-01-17 13:39:51.830701',1,'<p>haha</p>');
INSERT INTO "essay" VALUES(9,'haha','hoho','2016-01-17 13:41:09.146610',1,'<p>hoho</p>');
INSERT INTO "essay" VALUES(10,'hehe','haha','2016-01-17 13:41:57.907738',1,'<p>haha</p>');
INSERT INTO "essay" VALUES(11,'hehe','haha','2016-01-17 13:42:23.666786',1,'<p>haha</p>');
INSERT INTO "essay" VALUES(12,'hehe','haha','2016-01-17 13:42:53.618638',1,'<p>haha</p>');
INSERT INTO "essay" VALUES(13,'haha','hoho','2016-01-17 13:44:53.056607',1,'<p>hoho</p>');
INSERT INTO "essay" VALUES(14,'ceshi','dsfdfdsfnhsdcbsofbwob
cafssan

as

das

das

da
sd
w
q


wqwfwqfqw','2016-01-17 13:56:12.783701',1,'<p>dsfdfdsfnhsdcbsofbwob
cafssan</p>
<p>as</p>
<p>das</p>
<p>das</p>
<p>da
sd
w
q</p>
<p>wqwfwqfqw</p>');
CREATE UNIQUE INDEX ix_user_nickname ON user (nickname);
COMMIT;
