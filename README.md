

## Setup environment
1. Install hugo (https://gohugo.io/getting-started/installing/)

2.
```sh
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r ./requirements.txt
```

## Add a new publication
1. Update `assets/pubs/{conf, pub}.bib`.
2. Add `${paper}-abstract.md`, `${paper}-slides.pdf`, and `${paper}.pdf`
3. Then, run
```bash
$ ./bin/make_pub.py
```

## Add a new person
Please add your profile in `content/author`.

## Add news
Modify `content/home/news.md`.

## Reference
- https://github.com/wowchemy/starter-academic

