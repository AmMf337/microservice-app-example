# Assigment 1

The objective of this assigment is migrate the application of this repository to kubernetes using dockerfiles, deployments, configmaps and secrets, also to implement some tools of kubernetes like hpa and a deployment strategy as well as monitoring by grafana and prometheus.

### Dockerfiles

In this section it will be explain a general view of the composition of the docker files and some particular characteristics implement for some services.

The general structure of the dockerfiles is the following:

```yaml

FROM Image AS builder #An image mark as the phase of build for a ligther final image

WORKDIR /app # Directory for the app's archives


COPY ./directory ./ # Copy directory with the app's dpendencies
RUN npm dependencies # Install dependencies


COPY ./src ./src  # Copy source code
RUN npm  #Compilate code

# Final image
FROM openjdk:8-jre-alpine

WORKDIR /app # Directory for the app's archives

COPY --from=builder /app/target/*.jar app.jar

# Default enviroment variables
ENV SERVER_PORT=8083
ENV JWT_SECRET=myfancysecret
ENV SPRING_ZIPKIN_BASEURL=http://127.0.0.1:9411/

#Port
EXPOSE 8083

# Initialization
ENTRYPOINT ["java", "-jar", "app.jar"]

```
