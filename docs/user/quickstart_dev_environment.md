Download the Arista cEOS image `cEOS64-lab-4.32.1F.tar.xz` from [Arista's website](https://www.arista.com/en/support/software-download) and then run `docker import cEOS64-lab-4.32.1F.tar.xz ceos:4.32.1F` from the directory where this file was downloaded. Then you can proceed with the rest of the dev environment quick start below.

```bash
invoke build
invoke migrate start cli
nautobot-server generate_clab_test_data && exit
```

### Navigate to Lab Topology 

On the Nautobot Homepage, expand the "CONTAINERLAB" dropdown and click "Topologies".

![Navigation 1](../images/navigation_1.png)

Once on the list of topologies, click the `lab device` topology. 
![Navigation 2](../images/navigation_2.png)

Once on detail page, you have multiple boxes of information as well as a "Containerlab" actions button. This action button allows you to do the following:

- Deploy Containerlab topology from the presented topology file. 
- Destroy an already destroyed topology.
- Push the topology file to a git repo. 

![Topology Detail Action Button](../images/button_options.png)

Once a topology is deployed, you can connect to your devices via the "Connection Portal" table. All you need to do is click on the device's respective SSH symbol and a new tab will open dropping you into the device's CLI. 

> Note: You must first ensure you have Guacamole running by going through the [Guacamole](../admin/guacamole.md) documentation.

![Topology Detail Action Button](../images/topology_connections.png)