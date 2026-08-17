# SKU-Number Merge
My first personal and practical project using Python.

## Purpose
I was tasked with quickly synchronising the SKU-numbers of two massive inventories in two almost identical Shopify shops, so i build a safe, fast and responsive python script that did so. It wasn't a huge project, took about a week, but most of it was learning on the spot and double checking that i didn't mess anything up.

## How to use the scripts
It is comprised of running 5 scripts:

-1 Downloading the inventory of the shop in a CVS file*

-2 Updating the first of the shops inventory so each of their items has a unique SKU number

-3 Merging the current SKU-numbers of first shop with the second.

-4 Updating the SKU-numbers in the actual online Shopify inventories.

-5 Double checking that the update went through and that no complications happened, as well as a get a list of the few items in both inventories that are unique to the shop.

## Notes
*There are technically two of the first script, because the project was time sensitive as well as a one time solution, so instead of spending time on optimizing the first script to work for both shops, i instead just worked quick and copied it.

All the scripts give comprehensive feedback on what happened, and allows the user to spot inconsistencies.

It was both really interesting and fun as it was the first time i ever worked with Python, i therefor made a lot of use of AI, but i of course 


The .env file is obviously not included.
