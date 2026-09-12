"""
Database & Data Storage Detectors
====================================
Covers: MongoDB, MySQL, PostgreSQL, Redis, MariaDB,
        MSSQL, Oracle DB, Snowflake, Elasticsearch,
        InfluxDB, Neo4j, CockroachDB, PlanetScale,
        Neon, Supabase, Upstash, AMQP/RabbitMQ,
        FTP, LDAP, ODBC, DB2, Solr, Cassandra.
"""

import re

# fmt: off
DATABASE_DETECTORS = [

    # ════════════════════════════════════════════════════════════════════
    # MongoDB
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"mongodb(?:\+srv)?://[^:\s]+:[^@\s]+@[^/\s]+(?:/\S*)?"),
     "MongoDB Connection URI", "MongoDB", "data_storage", 1.0),

    (re.compile(r"mongodb(?:\+srv)?://[^:\s]+:[^@\s]+@"),
     "MongoDB Credentials", "MongoDB", "data_storage", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # MySQL
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"mysql://[^:\s]+:[^@\s]+@[^/\s]+(?:/\S*)?"),
     "MySQL Connection URI", "Oracle", "data_storage", 1.0),

    (re.compile(r"(?:DB_PASSWORD|MYSQL_PASSWORD|MYSQL_ROOT_PASSWORD)\s*[=:]\s*\S{6,}"),
     "MySQL Password Env Var", "Oracle", "data_storage", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # PostgreSQL
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"postgres(?:ql)?://[^:\s]+:[^@\s]+@[^/\s]+(?:/\S*)?"),
     "PostgreSQL Connection URI", "PostgreSQL", "data_storage", 1.0),

    (re.compile(r"(?:POSTGRES_PASSWORD|PG_PASSWORD|DATABASE_PASSWORD)\s*[=:]\s*\S{6,}"),
     "PostgreSQL Password Env Var", "PostgreSQL", "data_storage", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # Redis
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"redis://(?:[^:\s]+:[^@\s]+@)?[^/\s]+(?:/\d+)?"),
     "Redis Connection URI", "Redis", "data_storage", 1.0),

    (re.compile(r"rediss://[^:\s]+:[^@\s]+@[^/\s]+"),
     "Redis TLS Connection URI", "Redis", "data_storage", 1.0),

    (re.compile(r"(?:REDIS_PASSWORD|REDIS_AUTH)\s*[=:]\s*\S{8,}"),
     "Redis Password Env Var", "Redis", "data_storage", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # MSSQL / SQL Server
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"(?:Data Source|Server)=[^;]+;(?:Initial Catalog|Database)=[^;]+;User(?:\s*ID)?=[^;]+;Password=[^;]+"),
     "MSSQL Connection String", "Microsoft", "data_storage", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Snowflake
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"(?:SNOWFLAKE_PASSWORD|snowflake[_\-]?(?:password|private[_\-]?key))\s*[=:]\s*\S{8,}"),
     "Snowflake Credentials", "Snowflake", "data_storage", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # Elasticsearch
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"https?://[^:\s]+:[^@\s]+@[^:/\s]+(?::\d+)?/_cluster"),
     "Elasticsearch Credentials", "Elastic", "data_storage", 1.0),

    (re.compile(r"ApiKey\s+[A-Za-z0-9+/=]{30,}"),
     "Elastic API Key", "Elastic", "cloud_provider", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # InfluxDB
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"(?:INFLUX_TOKEN|INFLUXDB_TOKEN|influxdb[_\-]?token)\s*[=:]\s*[A-Za-z0-9+/=_\-]{80,}=="),
     "InfluxDB Token", "Influxdata", "data_storage", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # Supabase
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"sbp_[A-Za-z0-9]{40}"),
     "Supabase Personal Access Token", "Supabase", "data_storage", 1.0),

    (re.compile(r"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+"),
     "Supabase Service Role JWT", "Supabase", "data_storage", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # PlanetScale
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"pscale_tkn_[A-Za-z0-9_]{32}"),
     "PlanetScale Service Token", "PlanetScale", "data_storage", 1.0),

    (re.compile(r"pscale_pw_[A-Za-z0-9_]{32}"),
     "PlanetScale Database Password", "PlanetScale", "data_storage", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Neon (Serverless Postgres)
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"ep-[a-z0-9\-]+-[a-z0-9]+\.(?:us-east|eu-central|ap-southeast)-\d+\.aws\.neon\.tech"),
     "Neon Database Host (candidate)", "Neon", "data_storage", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # AMQP / RabbitMQ
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"amqps?://[^:\s]+:[^@\s]+@[^/\s]+(?:/\S*)?"),
     "AMQP/RabbitMQ Connection URI", "None", "data_storage", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # FTP
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"ftps?://[^:\s]+:[^@\s]+@[^/\s]+(?:/\S*)?"),
     "FTP Credentials URI", "None", "data_storage", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # LDAP
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"ldaps?://[^:\s]+:[^@\s]+@[^/\s]+(?:/\S*)?"),
     "LDAP Credentials URI", "None", "data_storage", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # ODBC
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"(?:Driver|DSN)=\{[^}]+\};.*?(?:Uid|User|UID)=[^;]+;.*?(?:Pwd|Password|PWD)=[^;]+"),
     "ODBC Connection String", "None", "data_storage", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # MariaDB
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"mariadb://[^:\s]+:[^@\s]+@[^/\s]+(?:/\S*)?"),
     "MariaDB Connection URI", "None", "data_storage", 1.0),

    # ════════════════════════════════════════════════════════════════════
    # Cassandra
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"(?:CASSANDRA_PASSWORD|cassandra[_\-]?password)\s*[=:]\s*\S{8,}"),
     "Cassandra Credentials", "Apache", "data_storage", 0.85),

    # ════════════════════════════════════════════════════════════════════
    # Upstash Redis
    # ════════════════════════════════════════════════════════════════════
    (re.compile(r"rediss://(?:default|[^:\s]+):[A-Za-z0-9]{120,}@[a-z0-9\-]+\.upstash\.io:\d+"),
     "Upstash Redis Connection URI", "None", "data_storage", 1.0),
]
# fmt: on
