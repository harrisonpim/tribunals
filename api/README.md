# API

REST API for querying concepts and documents from elasticsearch.

Run `make api` to start the API server in a container. The root endpoint `/` will the documentation for the API, including the available endpoints and their parameters.

The API depends on the elasticsearch service, which will need to be populated with data before the API can be used. The data can be indexed into elasticsearch by running the `make index` command.
