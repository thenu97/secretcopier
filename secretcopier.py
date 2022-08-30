from kubernetes import client, config


config.load_kube_config()


class SecretCopier:
    def __init__(self):
        print("Intialising SecretCopier...")
        self.api = client.CustomObjectsApi()
        self.v1 = client.CoreV1Api()
        self.contexts, _ = config.list_kube_config_contexts()

    def get_secrets(self):
        secrets = self.v1.list_namespaced_secret('default')
        certs = [secret for secret in secrets.items if secret.type ==
                 'kubernetes.io/tls']

        return certs

    def get_namespaces(self):
        namespaces = set()
        for namespace in self.v1.list_namespace().items:
            namespaces.add(namespace.metadata.name)

        return namespaces

    def create_secret(self, data, namespace, metadata_annotations, metadata_name):
        secret = client.V1Secret(
            api_version="v1",
            kind="Secret",
            metadata={"annotations": metadata_annotations,
                      "name": metadata_name, "namespace": namespace},
            data=data,
            type="kubernetes.io/tls",
        )

        api = self.v1.create_namespaced_secret(
            namespace=namespace, body=secret)

        return api

    def copier(self):
        for namespace in self.get_namespaces():
            print(namespace)
            for cert in self.get_secrets():
                self.create_secret(cert.data, namespace=namespace,
                                   metadata_annotations=cert.metadata.annotations, metadata_name=cert.metadata.name)


copy = SecretCopier()
copy.copier()
