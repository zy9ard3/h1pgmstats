## Description :

Currently, HackerOne lacks a feature to sort programs by `Bounties Paid in Last 90 Days` or `Reports Received in Last 90 Days`, This app can help to address that gap by fetching and displaying relevant data in a table format on your local instance along with sorting functionality

## Usage :

By default, this app has a [predefined URL](https://zy9ard3.github.io/h1pub.txt) only for public programs handles. For private program data ;

* collect all your program handles and create a secret gist for those via [Github Gist](https://gist.github.com) ( Recommended )

### How to collect all the handles ?

* you can use this awesome [bbscope](https://github.com/sw33tLie/bbscope) tool as follows ;
> ```bash
> bbscope h1 -t <your-h1-apikey> -u <your-h1-username> -a -b -o u|uniq|sed -E 's/^.*https:\/\/hackerone\.com\///g'|tee handles.txt
> ```

## Steps :

* Clone the repository
```bash
git clone https://github.com/zy9ard3/h1pgmstats.git
```
* Install the necessary packages
```bash
pip install flask requests
```
* Change to App directory
```bash
cd h1pgmstats
```
* Run the application
```bash
python h1pgmstats.py
```
* Navigate to http://127.0.0.1:5000
* For public program stats, just click `Run Unauthenticated`
* For private program stats, paste the `Gist Handles URL`, `CSRF Token` and `Cookie` inputs into their respective areas and click `Run Authenticated`
* Wait until the data is displayed
> > https://github.com/zy9ard3/dev/assets/67743789/3e350496-cc43-4c10-ac9a-49ae523c9a91

#### *If you encounter any issues, Feel free to contact me @ https://twitter.com/zy9ard3*
