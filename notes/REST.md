# REST

- What does it stand for?
  - Stands for Representational State Transfer.
<br></br>

- What does it do?
  - It is a protocol for a server to provide a client with data retrieval and storage services.
<br></br>

- Are there any other protocols similar to this?
  - RPC (remote procedure call) or SOAP (Simplified Object Access Protocol) are precedessors of REST
<br></br>

- What are six characteristics of REST?
  1. Client-server (A clear separation between clients and servers)
  2. Stateless (A server must not store any state/info about the client that persists between requests)
  3. Cache (Responses can be cached or non-cacheable so clients can use cache for optimization purposes)
  4. Uniform interface (The protocol by which clients access server resources must be consistent, well defined and standardized)
  5. Layered system (Proxy servers, caches or gateways can be placed between clients and servers to improve performance)
  6. Code-on-demand (clients can download code optionally from the server, for them to execute)
<br></br>

- What are resources in REST?
  - An item of interest in the domain of the application. e.g. User, Post, Comment instances of our app are all resources
  - Each resource must have a unique identifier e.g. a blog post is identified by a unique URL ```/api/posts/12345```
  - A collection of resources are identified with a URL that ends with a forward slash e.g. ```/api/posts/```
<br></br>

- What are the most common request methods by clients to an API in REST protocol?
  - Get (Read) (Returns 200 if successful)
  - Post (Create) (Returns 201 if successful)
  - Put (Update) (returns 200 or 204 if successful)
  - Delete (Delete) (returns 200 or 204 if successful)
<br></br>

- How are resources encoded in REST protocol usually?
  - Encoding are usually JSON or XML
<br></br>

- What does a request need in HTTP (https://www.toolsqa.com/client-server/http-request/)?
  - A request line, with Protocol, request URI, HTTP protocol version (see example below)
  - Headers
  - An empty line
  - Message body (optional)
<br></br>

- What does a request look like?
  - A GET request example:
  > GET /search?q=what HTTP/1.1  (this is the request line, data is set in the request URI)
  
  > (this is the header) </br>
    Host: google.com  </br>
    User-Agent: curl/7.75.0 </br>
    Accept: */*

  - A POST request example:
  > POST /test HTTP/1.1

  >Host: foo.example</br>
  Content-Type: application/x-www-form-urlencoded</br>
  Content-Length: 27

  >(this is the body)</br>
  field1=value1&field2=value

<br></br>
- What are the types that a POST method can have for its body?
  - The default is ```application/x-www-form-urlencoded``` as in example before, but a JSON can also be applied (https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST)
  - Make sure the type is what the server expects/can process!
<br></br>

- How can REST APIs remember clients that have provided login credentials, without having to ask them to store a cookie (like we did with Flask-Login? Many clients are not web browsers!
    - The client can put their credentials in the header of all their requests. 