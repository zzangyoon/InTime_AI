-- SQLite
select * from member_test 
where date(reg_date)="2025-09-17";

----------------------------------------
-- 날짜만 변경하는 쿼리 (|| : 문자열 연결)
----------------------------------------
-- update member_test 
-- set reg_date = "2025-09-19" || substr(reg_date, 11)
-- where id = 2;