namespace netstd automl
namespace py automl

struct HelloWorldStruct {
	1: string text
}

service HelloWorldService {
	void HelloWorld(HelloWorldStruct input)
}