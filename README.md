# cryosparc-examples
Example scripts, notebooks, and code snippets that are helpful for CryoSPARC users!

## 📜 How do I use these scripts?
These scripts can be run on your own computer or from the computer hosting CryoSPARC.
They all require `cryosparc-tools` and its dependencies.
For more information on installing `cryosparc-tools`, please see the [package documentation](https://tools.cryosparc.com/intro.html).

Some scripts also require `plotnine` for advanced plotting and `polars` for advanced data manipulation. See [the `plotnine` page](https://plotnine.org/) and [the `polars` page](https://pola.rs/) page for more information.
These packages are mostly used for plotting, so if you do not wish to install those packages you can simply remove the cells which require them and the scripts should largely remain functional.

Once dependencies are installed, you can run notebooks (`*.ipynb`) using your [Jupyter Notebook](https://jupyter.org/) environment of choice.
You can run python scripts (`*.py`) directly in the terminal in the usual way (`path/to/script.py` or `python path/to/script.py`).

## 💻 Where can I run these scripts from?
The scripts and notebooks do *not* need to be run on the master node --- they simply need to have access to the following ports:

 * The CryoSPARC base port (`39000` by default)
 * Base port + 2 (`39002` by default)
 * Base port + 3 (`39003` by default)
 * Base port + 5 (`39005` by default)

If the scripts are being run on the master node, these ports are open and the `host` parameter of `CryoSPARC()` can be set to `localhost`.
If the scripts are being run on a machine with direct network access to the master node *and* the above ports, `host` should be set to the master node's host name and `base_port` should be set to the appropriate base port (`39000`) by default.

If the scripts are being run from a machine without direct network access to the master node (e.g., a personal computer), you must first set up SSH tunnels to the appropriate ports, then set `host` to `localhost` and `base_port` to the tunneled base port.
For example, running the command

```
ssh -N -L 39000:localhost:39000 -L 39002:localhost:39002 -L 39003:localhost:39003 -L 39005:localhost:39005 << master host >>
```

with `<< master host >>` replaced by the hostname for the CryoSPARC master nodes will set up ssh tunnels for each of the (default) required ports, so that setting `host` to `localhost` will be sufficient to run the script.

## 🤔 What is `instance-info.json`?
To prove that you're an authorized user of your CryoSPARC installation, any CryoSPARC Tools script you run needs your username and password.
This is just the email and password you use to access the normal CryoSPARC GUI; you do not need to be an administrator or have special access to the installation.
The scripts also need to know the hostname and base port for the CryoSPARC installation.
We find it convenient to store all of this information in a JSON file in the user's home directory, called `instance-info.json`.
This file has the following content (including the opening and closing `{}`):

```{json}
{
        "license": "<< your license >>",
        "email": "<< the email you use to log into the CryoSPARC GUI >>",
        "password": "<< the password you use to log into the CryoSPARC GUI>>",
        "base_port": << the port used to connect to the CryoSPARC instance. If the default 39000 is used, this line can be removed>>,
        "host": "<< the host of the CryoSPARC instance >>"
}
```

with the relevant information replacing all text surrounded by and including `<< >>`.
If you prefer, you can instead manually enter this information into the `cs = CryoSPARC()` lines at the beginning of the script.
More information on creating and authenticating the `CryoSPARC` object can be found [here](https://tools.cryosparc.com/intro.html#usage).