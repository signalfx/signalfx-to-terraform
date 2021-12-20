# Deprecated

This tool is deprecated. Please use the [official Terraform provider](https://github.com/terraform-providers/terraform-provider-signalfx)'s [import](https://www.terraform.io/docs/commands/import.html) support in conjunction with [state show](https://www.terraform.io/docs/commands/state/show.html).

>ℹ️&nbsp;&nbsp;SignalFx was acquired by Splunk in October 2019. See [Splunk SignalFx](https://www.splunk.com/en_us/investor-relations/acquisitions/signalfx.html) for more information.

# SignalFx to Terraform Exporter

This is a tool for exporting SignalFx assets to Terraform. It aims to support all of the assets that are supported by the [SignalFx Terraform Provider](https://github.com/signalfx/terraform-provider-signalfx).

The resulting Terraform config (in HCL) is emitted on `STDOUT`.

**Note:** This is alpha quality. Patches welcome!

# TODO
* Output currently does *not* know how to generate per-asset names that are unique, just placeholders for now
* Some attributes emit comment placeholders
* Does not yet understand chart types other than List, Time and Single Value
* While it can emit dashboards, it doesn't quite grok the `chart` asset and emits them empty.
* Test it more, no testing has yet been done to verify the output
* I think realm works?

# Usage

Specify your SignalFx API key using the environment variable `SFX_AUTH_TOKEN`.

```
usage: export.py [-h] [--realm REALM] [--verbose] [--chart CHART]
                 [--dashboard DASHBOARD] [--detector DETECTOR] --name NAME

optional arguments:
  -h, --help            show this help message and exit
  --realm REALM
                        SignalFx Realm (defaults to none)
  --verbose             Be verbose
  --chart CHART         A chart to convert
  --dashboard DASHBOARD
                        A dashboard to convert
  --detector DETECTOR   A detector to convert
  --name NAME           Terraform name of resulting asset
  ```

# How It Works

Each asset has an accompanying [Jinja2](http://jinja.pocoo.org/) template. With the help of a few functions in the Python script, the template does most of the work of deciding how to turn the API's JSON representation into the one used by the Terraform provider. These are not 1:1 because it would be tedious to define Terraform in the same manner as the API.
