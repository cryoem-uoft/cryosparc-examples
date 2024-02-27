# cryosparc-examples
Example scripts, notebooks, and code snippets that are helpful for CryoSPARC users!

## 📜 How do I use these scripts?
These scripts can be run on your own computer or from the computer hosting CryoSPARC.
They all require `cryosparc-tools` and its dependencies.
For more information on installing `cryosparc-tools`, please see the [package documentation](https://tools.cryosparc.com/intro.html).
Some scripts also require `plotnine` for advanced plotting and `polars` for advanced data manipulation. See [the `plotnine` page](https://plotnine.org/) and [the `polars` page](https://pola.rs/) page for more information.

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