from kubernetes import client, config
from kubernetes.client.rest import ApiException
import os

class KubernetesClient:
    def __init__(self) -> None:
        self.__sessions = {}
        self.__ingress_name = "explainer-dashboard-dynamics-routes"
        self.__ingress_namespace = "omaml"
        if os.getenv("KUBERNETES_TYPE") == "local":
            annotation = {
                #local cluster
                "kubernetes.io/ingress.class": "nginx",
                "cert-manager.io/cluster-issuer": "selfsigned-issuer",
            }
        else:
            annotation = {
                #local cluster
                "cert-manager.io/cluster-issuer": "lets-encrypt-oma-ml",
            }
        self.__ingress_metadata = client.V1ObjectMeta(
            name=self.__ingress_name,
            namespace=self.__ingress_namespace,
            annotations=annotation
        )


    def __get_ingress_instance(self):
        with client.ApiClient(config.load_incluster_config()) as api_client:
            ingress_client = client.NetworkingV1Api(api_client)
            try:
                ingress = ingress_client.read_namespaced_ingress(
                    name=self.__ingress_name,
                    namespace=self.__ingress_namespace
                )
                # The Ingress exists, you can perform actions on it
                print("Ingress already exists:", ingress)
            except client.ApiException as e:
                # The Ingress doesn't exist, create it
                if e.status == 404:
                    client.NetworkingV1Api
                    ingress = client.V1Ingress(
                        metadata=self.__ingress_metadata,
                        spec=client.V1IngressSpec(
                            # Set the desired Ingress spec here
                            tls=[
                                client.V1IngressTLS(
                                    hosts=[
                                        os.getenv("KUBERNETES_URL")
                                    ],
                                    secret_name="kubernetes.docker.internal-tls"
                                )
                            ],
                            rules=[
                                client.V1IngressRule(
                                    host=os.getenv("KUBERNETES_URL"),
                                    http=client.V1HTTPIngressRuleValue(
                                        paths=[
                                            client.V1HTTPIngressPath(
                                                backend=client.V1IngressBackend(
                                                    service=client.V1IngressServiceBackend(
                                                        name="controller",
                                                        port=client.V1ServiceBackendPort(
                                                            number=12345
                                                        )
                                                    )
                                                ),
                                                #path="/dummy(/|$)(.*)",
                                                path="/dummy",
                                                path_type="Prefix"
                                            )
                                        ]
                                    )
                                )
                            ]
                        )
                    )
                    ingress = ingress_client.create_namespaced_ingress(
                        namespace=self.__ingress_namespace,
                        body=ingress
                    )
                    print("Ingress created:", ingress)
                else:
                    # An unexpected error occurred
                    raise e
        return ingress

    # Add a new path to the Ingress
    def add_path(self, path, automl_service, port):
        self.__ingress_instance = self.__get_ingress_instance()
        with client.ApiClient(config.load_incluster_config()) as api_client:
            self.__ingress_instance.spec.rules[0].http.paths.append(
                client.V1HTTPIngressPath(
                    backend=client.V1IngressBackend(
                        service=client.V1IngressServiceBackend(
                            name=automl_service,
                            port=client.V1ServiceBackendPort(
                                number=port
                            )
                        )
                    ),
                    path=f"/{path}",
                    path_type="Prefix"
                )
            )
            print(self.__ingress_instance)
            # Create or update the Ingress resource
            ingress_client = client.NetworkingV1Api(api_client)
            ingress_client.patch_namespaced_ingress(
                name=self.__ingress_name,
                namespace=self.__ingress_namespace,
                body=self.__ingress_instance
            )

    # Remove a path from the Ingress
    def remove_path(self, path):
        self.__ingress_instance = self.__get_ingress_instance()
        with client.ApiClient(config.load_incluster_config()) as api_client:
            print(f"DASHBOARD REMOVE PATH /{path}, currently PATH #{len(self.__ingress_instance.spec.rules[0].http.paths)}")
            self.__ingress_instance.spec.rules[0].http.paths = [
                p for p in self.__ingress_instance.spec.rules[0].http.paths if p.path != f"/{path}"
            ]
            print(f"DASHBOARD REMOVE PATH /{path}, new PATH #{len(self.__ingress_instance.spec.rules[0].http.paths)}")
            print(self.__ingress_instance)
            # Create or update the Ingress resource
            api_instance = client.NetworkingV1Api(api_client)
            api_instance.patch_namespaced_ingress(
                name=self.__ingress_name,
                namespace=self.__ingress_namespace,
                body=self.__ingress_instance
            )
