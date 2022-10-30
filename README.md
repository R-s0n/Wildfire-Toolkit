# Wildfire-Toolkit

_NOTE: This framework is designed to be used with the [WAPT Framework](https://github.com/R-s0n/WAPT_Framework)_

The Wildfire Toolkit is a collection of python scripts designed to perform a **wide** range of recon, enumeration, and security scanning against a list of Fully-Qualified Domain Names (FQDNs), more commonly referred to as "Seeds" or "Roots" in bug bounty hunting.  This toolkit works by running various modules through the `wildfire.py` script.  A list of FQDNs is pulled from the [WAPT Framework](https://github.com/R-s0n/WAPT_Framework) and used as a starting point for various pen testing techniques.  The results of these scripts are then sent back to the Framework to be stored and managed as needed.

*Check out my LinkedIn posts like [this one](https://www.linkedin.com/feed/update/urn:li:activity:6849314055283466240/) for more information on how I search for bugs and where this framework falls into the bigger picture of my methodology!*

### Install

*I recommend installing this framework on a clean and fully updated version of [Kali Linux](https://www.kali.org/get-kali/)*

`python3 install.py`

### Run

The Wildfire Toolkit has a variety of modules to accomplish different tasks.  In most cases, you will need to run the modules in order, although some (like the Fire Spreader module) are not required.

#### Fire Starter (`--start`)

The Fire Starter module is designed to conduct Recon on the FQDN, looking for all available Subdomains for that Seed/Root.  These scripts use several different open-source tools to search for subdomains in three discinct ways:
1. Scraping Public Resources (Google Dorking, Wayback Machine, etc.)
2. Crawling Known Domains (<a href>, JavaScript links, etc.)
3. Subdomain Brute Forcing
Once a list of possible subdomains has been discovered, the Fire Starter module consolidates this list into unique subdomains and probes each domain to see if it is hosing a live web server that can be accessed a client.

**Desired Result: A list of live URLs that can be scanned for CVEs and inspected for possible manual testing**

#### Fire Spreader (`--spread`)

This Fire Spreader module works similar to the Fire Starter module, with the only difference being that these scripts focus on discovering IP Addresses and Port Numbers associated with the FQDN that have web servers running on various ports that may not be listed in DNS.  Once discovered, these can be treated as any other URL for further testing, with the obvious difference being that the URL will contain and IP Address and Port Number in place of a Domain (Ex: https://123.456.789.123:8888).

**Desired Result: A list of live IP/Port combinations that can be scanned for CVEs and inspected for possible manual testing**

#### Fire Scanner (`--scan`) <- *Really need to think of a creative name for this, eventually...*

This Fire Scanner module is designed to find possible CVEs on all live URLs and IP/Port combinations discovered the Fire Starter and Fire Spreader modules.  Currently, this module works in three stages:
1. Uses Nuclei to scan for known CVEs and other misconfigurations outlined in the Nuclei Templates, as well as [Custom Templates](https://github.com/R-s0n/Custom_Vuln_Scan_Templates) I have built myself.
2. Checks for client-side JavaScript libraries with known vulnerabilities.
3. Checks for Prototype Pollution using a variation of my [Green Energy](https://github.com/R-s0n/Green-Energy) scanner.

**Desired Result: Discover possible vulnerabilities that the user can later manually validate and report**

#### Fire Enummerator (`--enum`) <- *Seriously, gotta think of a better name here...*

This Fire Enummerator module crawls the `Target URL` that is identified by the user in the WAPT Framework.  Once the user has decided on a specific URL that looks like it may have Common Weakness Enumerations (CWEs) that can be reported, that user will set that URL as the `Target URL` in the WAPT Framework.  Only one `Target URL` can be set for a FQDN at a time.  This module pulls a list of URLs, one for each FQDN, and thorougly enumerates that target.  The module uses a custom crawler that works in three phases over several cycles:
1. Parse the HTML and JavaScript contained in raw HTML responses to identify new endpoints to crawl
2. Uses specially crafted wordlists to brute force additional endpoints
3. Uses a headless browser to load the application, monitor for DOM changes, and parse the DOM as it changes to identify new endpoints (designed for Single Page Application (SPA) crawling)
Once a list of endpoints has been found, this module attempts to discover any Parameters (including hidden parameters) that can be used as an  Attack Vector for Dynamic Application Security Testing (DAST) scanning and manual penetration testing.  Finally, all requests can (and should!) be routed through a Burp Proxy for futher testing.

**Desired Result: Identify a list of endpoints, as well as paramters that can be used with that endpoint, to act as Attack Vectors for later testing**
