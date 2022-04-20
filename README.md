# Task: Postgres Pipeline

Imagine you have 2 databases. One corresponds to application database (app_db) and
the second one to analytical database (anal_db). In order for analytics guys to work with
the data produced by application, data needs to be transferred.

Your task is to create the tool for data pipeline! It's a real-world use-case, but a bit
simplified to not bother with all low-level db stuff (for now, heh). 

What it should do ?

1. Copy data from 1 table in 1 src db, to 1 table in 1 dst db. DB is only postgres.
2. Create dst table if not exists, which should look like the src table
3. Create indexes/primary keys according to specification
4. Solve conflicts - in case data are being updated and we re-run the tool, it should only
   update the changed data, not append or delete, or anything else. Just update changes. 


# Tests

Simply said, imagine doing TDD, your task now is, to pass all tests. 
Look at enclosed file `tests.py`. Finish `PostgresTransfer` class so that
the test `test_transfer_simple` pass.

## Run DBs

To create databases run: `docker-compose up -d`. You should have up and running 2 postgres
databases at localhost ports `54320` (app_db) and `54321` (anal_db).

Note: If you don't have docker or struggle with installing, make it work (windows...) 
feel free to create local databases and edit `APP_DB_URI` and `ANAL_DB_URI` if needed. 

## Run tests

In `requirements.txt` you have everything you need to run tests. Install it via pip, then run 
`pytest tests.py`, when tests will pass, you are finished (:

# Additional questions

1. Imagine the data are too big. You can't do `select *` on them everytime you want to transfer
   data, its gonna take ages. Your goal is to have all the data in analytical database. 
   How would you solve such a problem?

2. What problems do you see with `PostgresTransfer` (except 1. question :D). Is there anything you 
   would do other way in `PostrgresTransfer`? Is there anything you would automatize 
   for user (dev) who is using your tool (change API, gen code, basically whatever)? 

# Summary

1. Finish `PostgresTransfer` class
2. Make all tests pass
3. You can use whatever you want. Do not edit `tests.py`, except the db_uri if needed.
4. If you enclose your own tests (unit/integration), big up.
5. Answer Questions

If you would find out some bug in tests/docker etc. or you feel like you are stuck and you need 
help. Don't hesitate to contact us. 

If you give us little review about the task itself, we will be happy.

Prepare yourself, you will be writing code! Task itself is not so hard.
There are no catch questions or anything. Main point is to find out your 
design thinking (especially software), problem solving capabilities and some
basic usage of db.
