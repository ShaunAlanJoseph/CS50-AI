import os
import random
import re
import sys

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

    links_on_page = corpus[page]
    if not links_on_page:
        links_on_page = corpus.keys()
    links_count = len(links_on_page)

    pages_count = len(corpus)
    to_random_page = (1 - damping_factor) / pages_count
    through_link = damping_factor / links_count

    distribution = dict()
    for current_page in corpus.keys():
        distribution[current_page] = to_random_page
        if current_page in links_on_page:
            distribution[current_page] += through_link

    return distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    freq = dict()
    distribution = dict()
    pages_count = len(corpus)
    for page in corpus.keys():
        freq[page] = 0
        distribution[page] = 1 / pages_count

    for i in range(n):
        chosen_page = random.choices(list(distribution.keys()), weights=list(distribution.values()), k=1)[0]
        freq[chosen_page] += 1
        distribution = transition_model(corpus, chosen_page, damping_factor)

    pagerank = dict()
    for page, f in freq.items():
        pagerank[page] = f / n

    return pagerank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    distribution = dict()
    inc_pages = dict()
    pages_count = len(corpus)
    for page in corpus.keys():
        distribution[page] = 1 / pages_count
        inc_pages[page] = list()

    for page in corpus.keys():
        links = corpus[page]
        if len(links) == 0:
            links = corpus.keys()
        for link in links:
            inc_pages[link].append(page)

    significant_change = True
    while significant_change:
        significant_change = False
        for page in corpus.keys():
            part1 = (1 - damping_factor) / pages_count
            part2 = 0
            for inc_page in inc_pages[page]:
                links_on_inc_page = len(corpus[inc_page]) if len(corpus[inc_page]) else len(corpus)
                part2 += distribution[inc_page] / links_on_inc_page
            part2 *= damping_factor
            if abs(distribution[page] - part1 - part2) > 0.0001:
                significant_change = True
            distribution[page] = part1 + part2

    return distribution


if __name__ == "__main__":
    main()
