# Assigment 1

The objective of this assigment is migrate the application of this repository to kubernetes using dockerfiles, deployments, services, configmaps and secrets, also to implement some tools of kubernetes like hpa and a deployment strategy as well as monitoring by grafana and prometheus.

### Dockerfiles

In this section it will be explain a general view of the composition of the dockerfiles.

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

COPY --from=builder /app/target/*.jar app.jar #Copy the compile code

# Default enviroment variables
ENV SERVER_PORT=8083
ENV BASEURL=http://127.0.0.1:9411/

#Port
EXPOSE 8083

# Initialization
ENTRYPOINT ["java", "-jar", "app.jar"]

```

### Deploymets

As above, a general structure will be explain and for the case of frontend an explanation of extra characteristics implemented.

Then define each deployment and it's respective service,for simplicity we will explain the common parts of the deployment and service:
### Deployment
```yaml
metadata:
  name: <deployment-name>
  namespace: <namespace>
```
- **name**: Unique identifier for this deployment
- **namespace**: Logical isolation where the deployment lives
```yaml
spec:
  replicas: 1
  selector:
    matchLabels:
      app: <app-name>
```
- **replicas**: Number of pods running the app
- **matchLabels**: The label that identify to which deployment the pod belongs to.
```yaml
spec:
      containers:
      - name: <container-name>
        image: <image:tag>
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: <port>
```
- **name**: Name of the container
- **image**: Docker image to use (e.g., nginx:alpine, postgres:15)
- **imagePullPolicy**: Policy that controls how to access the image . It has three possible values:
  - IfNotPresent = Only download if not already on the node
  - Always = Always pull the latest image
  - Never = Must exist locally
- **containerPort**: Port where the application inside the container listens

Some applications need a initial configuration of variables, those variables are define en the section **env**:
```yaml
     env:
        - name: DB_HOST
          value: "database-service.database-ns.svc.cluster.local"
        - name: DB_USER
          value: "postgres"
```
### Service

In this case the manifest of each service was include in the manifest of it's respective deployment.

```yaml
metadata:
  name: <service-name>
  namespace: <namespace>
```
- **name**: Becomes the DNS name for the service
```
spec:
  type: <type>
```
There are three types of service that determinates how it is exposed: ClusterIP,NodePort and LoadBalancer
- **ClusterIP**: Only allow communication inside the cluster
- **NodePort**: Allows communication between different nodes
- **LoadBalancer**: Allows communication from outside the cluster and also allows to distribute the workload between the pods of a service.

```yaml
selector:
    app: <app-name>
```
- Indicates the label of the pods where the services will send traffic to.
```yaml
  ports:
  - port: 80
    targetPort: 80
    nodePort: 30080  # Only for NodePort type
```
- **port**: Port where other services/pods connect to this service
- **targetPort**: Port on the container where traffic is sent
- **nodePort**: Port exposed on the physical node. Range: 30000-32767
### Frontend: Hpa and deployment strategy:

The manifest for the deployment of frontend has two additional characteristics implemented, horizontal pod scaler and an deployment strategy:

#### ***HPA*** :
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: frontend-hpa
  namespace: microservices
  labels:
    app: frontend
    component: frontend
    tier: presentation
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: frontend
  minReplicas: 1
  maxReplicas: 3
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 20
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 20
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
      - type: Pods
        value: 1
        periodSeconds: 60
      selectPolicy: Min
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 30
        periodSeconds: 30
      - type: Pods
        value: 4
        periodSeconds: 30
      selectPolicy: Max
```

The main parts are:

- **Maximun and minimun of replicas** : This define which is the minimun and maximun number of replicas the HPA can upScale or downScale:

```yaml
minReplicas: 1
maxReplicas: 3
```

**Metrics**: In this field we define the resources which state will define when to scale or descale the number of pods:
  
```yaml
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 20
- type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 20
```

- **type:Resource**: Indicates this metric is based on Kubernetes resource requests.
- **name**: Name of the resource. 
- **averageUtilization**: is the threshold that will trigger the HPA.Once it is surpassed it triggers the HPA.
- **type:Utilization**: The kind of aspect that will be measure, in this case utilization.

- **behavior**: This section controls how fast and the agressiveness of the up scale or doewn scale of pods:

```yaml
 scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10  Allow to remove 10% of pods
        periodSeconds: 60
      - type: Pods
        value: 1 Allow to remove 1 pod
        periodSeconds: 60
      selectPolicy: Min
scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 30 # Allow to add 30% of pods
        periodSeconds: 30 
      - type: Pods
        value: 4 # Allow to add 4 pods
        periodSeconds: 30
      selectPolicy: Max
```
It is divide in up scaling and down scaling but has the same variables and attributes: 

- **stabilizationWindowSeconds**: Time of reaction to trigger the up or down scale.
- **policies**: The quantity of pods that will be up or down scale.
    - type: It is the way the quantity of pods will be measure, percentage or the absolute value of pods.
- **selectPolicy**: Define which policy will be use. **Max** will choose the policy that allow to add or remove the most quantity of pods, **Min** will choose the one that sclae the least quantity of pods.
- **periodSeconds**: Window of time to remove or add pods.

### ConfigMaps

The configmaps contain enviorment variables for the configuration of the deployments such as url for connection with other deployments or configurations of internal processes or subprograms.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: deploy-config
  namespace: microservices
  labels:
    app: deploy-api
    component: backend
    tier: data
data:

  SERVER_PORT: "8083"
  
  APPLICATION_NAME: "users-api"
  
  OTHERSERVICE_BASEURL: "http://service:9411/"

```
It has similar components to deployments and services but it's special field is the field of data where different variables are declarate with the format NAME=VALUE, this notation allows as to declare variables for different propose
