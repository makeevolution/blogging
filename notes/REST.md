# REST

- What does it stand for?
  - Stands for Representational State Transfer.
- What does it do?
  - It is a protocol for a server to provide a client with data retrieval and storage services.
- Are there any other protocols similar to this?
  - RPC (remote procedure call) or SOAP (Simplified Object Access Protocol) are precedessors of REST
- What are six characteristics of REST?
  1. Client-server (A clear separation between clients and servers)
  2. Stateless (A server must not store any state/info about the client that persists between requests)
  3. Cache (Responses can be cached or non-cacheable so clients can use cache for optimization purposes)
  4. Uniform interface (The protocol by which clients access server resources must be consistent, well defined and standardized)
  5. Layered system (Proxy servers, caches or gateways can be placed between clients and servers to improve performance)
  6. Code-on-demand (clients can download code optionally from the server, for them to execute)
- What are resources in REST?
  - An item of interest in the domain of the application. e.g. User, Post, Comment instances of our app are all resources
  - Each resource must have a unique identifier e.g. a blog post is identified by a unique URL ```/api/posts/12345```
  - A collection of resources are identified with a URL that ends with a forward slash e.g. ```/api/posts/```
- What are the most common request methods by clients to an API in REST protocol?
  - Get (Read) (Returns 200 if successful)
  - Post (Create) (Returns 201 if successful)
  - Put (Update) (returns 200 or 204 if successful)
  - Delete (Delete) (returns 200 or 204 if successful)
- How are resources encoded in REST protocol usually?
  - Encoding are usually JSON or XML

- How can REST APIs remember clients that have provided login credentials, without having to ask them to store a cookie (like we did with Flask-Login? Many clients are not web browsers!
    - The client can put their credentials in the header of all their requests. 