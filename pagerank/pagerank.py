import os
import random
import re
import sys
import copy
import icecream

DAMPING = 0.85
SAMPLES = 10000


def main():

    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    #list of sites
    sites = list(corpus.keys())

    distribution = dict()
    #assigning each site its probability
    if not corpus[page]:
        corpus[page] = corpus.keys()
    else:

        # probabilities of each of two cases
        random_prob = (1 - damping_factor) / len(sites)
        choice_prob = damping_factor / len(corpus[page])

        for element in sites:
            if element in corpus[page]:
                distribution[element] = choice_prob+random_prob
            else:
                distribution[element] = random_prob


    return distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    PageRank = dict()

    for element in corpus.keys():
        PageRank[element] = 0



    PageRank[element] += 1/n
    sample = random.choice(list(corpus.keys()))
    #sampling
    if n > 1:
        for _ in range(n-1):
            #choosing new sample
            try:
                sample = random.choices(population= list(transition_model(corpus, sample, damping_factor).keys()),
                                        weights= list(transition_model(corpus, sample, damping_factor).values()),
                                        k = 1)[0]
            except ValueError:
                sample = random.choices(population=list(transition_model(corpus, sample, damping_factor).keys()),
                                        weights=list(transition_model(corpus, sample, damping_factor).values()),
                                        k=1)[0]


            PageRank[sample] += 1/n


    return PageRank

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    n = 1/len(corpus.keys())
    PageRank = dict()

    for element in corpus.keys():
        PageRank[element] = n
    #add elements to sites with no links
    for element in corpus.values():
        if not element:
            element.add(corpus.keys())

    #corpus.keys() = PageRank.keys()
    #corpus = {1html: {2html}, 2html: {1html ,3html}, 3html: {2html ,4html}, 4html:{2html}}
    #PageRank = {1html: {1/n},2html:{1/n},3html: {1/n}4.html:{1/n}}

    sites = list()
    # cpy = {1html: {1/n},2html:{1/n},3html: {1/n}4.html:{1/n}}
    i = 0
    while True:
        #copies previous state of PageRank
        cpy = copy.deepcopy(list(PageRank.values()))
        for site in PageRank.keys():
            for key, value in corpus.items():
                #check is site contains link to site which page rank is currenty calculated for
                if site in value:
                    sites.append(key)

            #calculates pagerank for each page
            sm = 0
            if sites:
                for tile in sites:
                    sm +=(PageRank[tile]/len(corpus[tile]))


                PR = (1-damping_factor)/len(corpus.keys()) + (damping_factor *  sm)
                PageRank[site] = PR
            sites.clear()

        #checks if all PageRank values change by more than 0.001
        sub = [x-y for (x,y) in zip(cpy, list(PageRank.values()))]
        if all([True if element > -0.001 else False for element in sub]):
            break

    return PageRank


if __name__ == "__main__":
    main()
