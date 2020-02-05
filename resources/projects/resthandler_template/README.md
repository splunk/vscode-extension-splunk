CREATE:
`curl -k -u <USERNAME>:<PASSWORD> -X POST https://<HOST>:8089/servicesNS/nobody/example_rest/example_eai_handler -d name=new -d custom_parameter=<CUSTOM_VALUE>`

GET:
`curl -k -u <USERNAME>:<PASSWORD> https://<HOST>:8089/servicesNS/nobody/example_rest/example_eai_handler/<STANZA_NAME>`
OR
`| rest /servicesNS/nobody/example_rest/example_eai_handler/new`

LIST:
`curl -k -u <USERNAME>:<PASSWORD> https://<HOST>:8089/servicesNS/nobody/example_rest/example_eai_handler`
OR
`| rest /servicesNS/nobody/example_rest/example_eai_handler`

EDIT:
`curl -k -u <USERNAME>:<PASSWORD> -X POST https://<HOST>:8089/servicesNS/nobody/example_rest/example_eai_handler/<STANZA_NAME> -d custom_parameter=<CHANGED_VALUE>`

DELETE:
`curl -k -u <USERNAME>:<PASSWORD> -X DELETE https://<HOST>:8089/servicesNS/nobody/example_rest/example_eai_handler/<STANZA_NAME>`