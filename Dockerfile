# server setup

# 1 : setup Docker Kernal + Python 
FROM python:3.12-slim

# 2 show django log 
ENV PYTHONUNBUFFERD = 1

# 3 update kernal 
RUN apt-get update && apt-get -y install gcc libpq-dev

# 4 create working dir 
WORKDIR /app

# 5 copy requirments 
COPY requirments.txt /app/requirments.txt  

# 6 install requirments 
RUN pip install --no-cache-dir -r /app/requirments.txt

# 7 copy all file into the system 
COPY . /app/