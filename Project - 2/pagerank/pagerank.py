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

    distribution = dict()
    for current_page in corpus.keys():
        distribution[current_page] = (1 - damping_factor) / len(corpus)

    links_on_page = corpus[page]
    if len(links_on_page) == 0:
        links_on_page = corpus.keys()
    link_probability = damping_factor / len(links_on_page)
    for current_page in links_on_page:
        distribution[current_page] += link_probability

    return distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    page_frequency = dict()
    current_model = dict()
    page_count = len(corpus)
    for page in corpus.keys():
        page_frequency[page] = 0
        current_model[page] = 1 / page_count

    for i in range(n):
        page_list = list(current_model.keys())
        page_probabilities = list(current_model.values())
        chosen_page = random.choices(page_list, weights=page_probabilities, k=1)[0]
        page_frequency[chosen_page] += 1
        current_model = transition_model(corpus, chosen_page, damping_factor)

    pagerank = dict()
    for page, freq in page_frequency.items():
        pagerank[page] = freq / n

    return pagerank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    pagerank = dict()
    inc_pages = dict()
    page_count = len(corpus)
    for page in corpus.keys():
        pagerank[page] = 1 / page_count
        inc_pages[page] = list()

    for page, links in corpus.items():
        for link in links:
            inc_pages[link].append(page)

    significant_change = True
    while significant_change:
        significant_change = False
        for page in corpus.keys():
            part1 = (1 - damping_factor) / page_count
            part2 = 0
            for inc_page in inc_pages[page]:
                part2 += pagerank[inc_page] / len(corpus[inc_page])
            part2 *= damping_factor

            if abs(pagerank[page] - (part1 + part2)) >= 0.0001:
                significant_change = True

            pagerank[page] = part1 + part2

    return pagerank


if __name__ == "__main__":
    main()
