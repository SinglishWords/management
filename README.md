# Management

## How to use this repo?

There are two main functions

* add/update questions;
* export all data;

For more information, check the `libs/database.py` .

### For add/update questions

#### Step 1.

Upload question list to the `./input/list.txt` file, the format should be one word in one line,

```
4d
5c's
6c's
a bit the
a jay
aa
aapu
aathaa
abalone
abang
abang berg
abang bod
abang body
abang sapau
```

Or you can put it in any file as you want, but make sure you change [the code in `Data%20Refresh.ipynb` file, under `Read-questions` section](./Data%20Refresh.ipynb#Read-questions) so that the program can read the right questions list in the notebook.


#### Step 2.

Follow the notebook, refresh the question list in the mysql database first, our script will set all the questions `enable` to be false, and then try to insert or enable all the words in the new word list.

We won't just delete the old questions in the mysql, since some answers rely on existing question's ID.

#### Step 3.

Still, follow the notebook, our app will sample questions from the redis, so we need to refresh the cache.


### For Data export.

I provide two different ways to export all the data, the first method is to export them as a pandas dataframe, and them we can export data to csv files or json files. I also give 2 simple example for the data analysis, just using pandas join functions.


## About config and settings

Update the config part in each notebook.
