{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "%matplotlib inline"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "from sklearn.decomposition import PCA\n",
    "from sklearn.manifold import TSNE\n",
    "import umap\n",
    "import pandas as pd\n",
    "import seaborn as sns\n",
    "import matplotlib.pyplot as plt\n",
    "from optparse import OptionParser, OptionGroup\n",
    "\n",
    "parser = OptionParser()\n",
    "parser.add_option(\"-f\", \"--file\", \n",
    "                  dest=\"filename\",\n",
    "                  help=\"Matrix with observations as rows and variables as columns.\",\n",
    "                  action=\"store\",\n",
    "                  metavar=\"FILE\")\n",
    "parser.add_option(\"-d\", \"--delimiter\",\n",
    "                  dest=\"delimiter\",\n",
    "                  help=\"Delimiter to use. Options are 'tab', 'comma' or 'semicolon'. [default: %default]\",\n",
    "                  action=\"store\",\n",
    "                  choices=[\"tab\", \"comma\", \"semicolon\"],\n",
    "                  default=\"tab\")\n",
    "parser.add_option(\"-c\",\n",
    "                  action=\"store_true\", \n",
    "                  dest=\"has_colnames\",\n",
    "                  help=\"Flag to indicate that the first row of the matrix is a header. [default: %default]\",\n",
    "                  default=True)\n",
    "parser.add_option(\"-r\", \n",
    "                  action=\"store_true\", \n",
    "                  dest=\"has_rownames\",\n",
    "                  help=\"Flag to indicate that the first column of the matrix contains rownames. [default: %default]\",\n",
    "                  default=True)\n",
    "parser.add_option(\"-m\", \"--methods\",\n",
    "                  dest=\"methods\",\n",
    "                  help=\"String specifying combination of dimensionality reduction methods to execute. 'P' for PCA, 'T' for tSNE, 'U' for UMAP. [default: %default]\",\n",
    "                  default=\"PTU\",\n",
    "                  metavar=\"COMBINATION\")\n",
    "parser.add_option(\"-g\", \"--group\",\n",
    "                  dest=\"group\",\n",
    "                  help=\"File containing a single column with no header to color the observations (in the same order).\",\n",
    "                  metavar=\"LABEL_FILE\")\n",
    "parser.add_option(\"--group_rownames\",\n",
    "                  action=\"store_true\",\n",
    "                  dest=\"group_rownames\",\n",
    "                  help=\"Flag to indicate that the label file has rownames. [default: %default]\",\n",
    "                  default=False)\n",
    "parser.add_option(\"--group_header\",\n",
    "                  action=\"store_true\",\n",
    "                  dest=\"group_colnames\",\n",
    "                  help=\"Flag to indicate that the label file has a header. [default: %default]\",\n",
    "                  default=False)\n",
    "parser.add_option(\"-o\", \"--outfile\",\n",
    "                  dest=\"outfile\",\n",
    "                  help=\"Path for output file in pdf format. [default: %default]\",\n",
    "                  metavar=\"OUTPUT_FILE\",\n",
    "                  default=\"out.pdf\")\n",
    "\n",
    "group = OptionGroup(parser, \"Dimensionality reduction parameters\")\n",
    "group.add_option(\"-s\", \"--scale\", \n",
    "                 action=\"store_true\",\n",
    "                 dest=\"scale\",\n",
    "                 help=\"Standardize data to zero mean and unit variance. [default: %default]\",\n",
    "                 default=False)\n",
    "group.add_option(\"--tsne_perplexity\",\n",
    "                 action=\"store\",\n",
    "                 dest=\"tsne_perplexity\",\n",
    "                 help=\"Perplexity parameter for tSNE. [default: %default]\",\n",
    "                 default=30,\n",
    "                 type=\"int\")\n",
    "group.add_option(\"--tsne_angle\",\n",
    "                 action=\"store\",\n",
    "                 dest=\"tsne_angle\",\n",
    "                 help=\"Angle parameter for tSNE. [default: %default]\",\n",
    "                 default=0.5,\n",
    "                 type=\"float\")\n",
    "group.add_option(\"--umap_neighbors\",\n",
    "                 action=\"store\",\n",
    "                 dest=\"umap_neighbors\",\n",
    "                 help=\"Number of neighbors to use in UMAP. [default: %default]\",\n",
    "                 default=15,\n",
    "                 type=\"int\")\n",
    "group.add_option(\"--umap_distance\",\n",
    "                 action=\"store\",\n",
    "                 dest=\"umap_distance\",\n",
    "                 help=\"Effective minimum distance between observations in UMAP. [default: %default]\",\n",
    "                 default=0.01,\n",
    "                 type=\"float\")\n",
    "group.add_option(\"--umap_metric\",\n",
    "                 action=\"store\",\n",
    "                 dest=\"umap_metric\",\n",
    "                 help=\"Metric to use in UMAP. [default: %default]\",\n",
    "                 default=\"euclidean\",\n",
    "                 type=\"string\")\n",
    "parser.add_option_group(group)\n",
    "\n",
    "group2 = OptionGroup(parser, \"Graphical output parameters\")\n",
    "group2.add_option(\"--height\", \n",
    "                 action=\"store\",\n",
    "                 dest=\"height\",\n",
    "                 help=\"Plot height in inches. Width is calculated so that each facet has an aspect ratio of 1 with respect to the height. [default: %default]\",\n",
    "                 default=8,\n",
    "                 type=\"float\")\n",
    "group2.add_option(\"--font_scale\",\n",
    "                  action=\"store\",\n",
    "                  dest=\"font_scale\",\n",
    "                  help=\"Font scale (1=small, 5 = large). [default: %default]\",\n",
    "                  default=2,\n",
    "                  type=\"float\")\n",
    "group2.add_option(\"--marker_size\",\n",
    "                  action=\"store\",\n",
    "                  dest=\"marker_size\",\n",
    "                  help=\"Marker size. [default: %default]\",\n",
    "                  default=50,\n",
    "                  type=\"float\")\n",
    "parser.add_option_group(group2)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "def dimred(X, label=None, scale=False, methods=\"PTU\", tsne_perplexity=30, tsne_angle=0.5, umap_neighbors=15,\n",
    "           umap_distance=0.01, umap_metric=\"euclidean\"):\n",
    "    \n",
    "    methods = [x for x in methods]\n",
    "    random_state=1\n",
    "    \n",
    "    if \"P\" in methods:\n",
    "        pca_fit = PCA(n_components=2, random_state=random_state).fit_transform(X)\n",
    "        pca_fit = pd.DataFrame(pca_fit, columns = [\"X\", \"Y\"])\n",
    "        pca_fit[\"method\"] = \"PCA\"\n",
    "        pca_fit[\"label\"] = pd.Series(label, index = pca_fit.index)\n",
    "    else:\n",
    "        pca_fit = None\n",
    "\n",
    "    if \"T\" in methods:\n",
    "        tsne_fit = TSNE(n_components=2, perplexity=tsne_perplexity, angle=tsne_angle, \n",
    "                        random_state=random_state).fit_transform(X)\n",
    "        tsne_fit = pd.DataFrame(tsne_fit, columns=[\"X\", \"Y\"])\n",
    "        tsne_fit[\"method\"] = \"tSNE\"\n",
    "        tsne_fit[\"label\"] = pd.Series(label, index = tsne_fit.index)\n",
    "    else:\n",
    "        tsne_fit = None\n",
    "\n",
    "    if \"U\" in methods:\n",
    "        umap_fit = umap.UMAP(n_neighbors=umap_neighbors, min_dist=umap_distance, \n",
    "                             metric=umap_metric, random_state=random_state).fit_transform(X)\n",
    "        umap_fit = pd.DataFrame(umap_fit, columns=[\"X\", \"Y\"])\n",
    "        umap_fit[\"method\"] = \"UMAP\"\n",
    "        umap_fit[\"label\"] = pd.Series(label, index = umap_fit.index)\n",
    "    else:\n",
    "        umap_fit = None\n",
    "\n",
    "    final_df = pd.concat([pca_fit, tsne_fit, umap_fit], axis = 0)\n",
    "    \n",
    "    return(final_df)\n",
    "\n",
    "def dimred_plot(coordinates, plot_height, plot_fontscale, plot_markersize, outfile):\n",
    "    sns.set(font_scale=plot_fontscale)\n",
    "    g = sns.FacetGrid(coordinates, col=\"method\", sharex=False, sharey=False, hue=\"label\", \n",
    "                      height = plot_height, aspect=1)\n",
    "    g.map(plt.scatter, \"X\", \"Y\", alpha=.7, s = 50)\n",
    "    g.add_legend()\n",
    "    g.fig.savefig(outfile, bbox_inches=\"tight\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "if __name__ == \"__main__\":\n",
    "    #args = [\"-f\", \"file.tsv\", \"-g\", \"y.tsv\", \"--group_rownames\", \"--group_header\"]\n",
    "    (options, args) = parser.parse_args(args)\n",
    "    sep_dict = {\"tab\": \"\\t\", \"comma\": \",\", \"semicolon\":\";\"}\n",
    "\n",
    "    # TODO: Do argument checking here\n",
    "    pass\n",
    "\n",
    "    # Read input data\n",
    "    data = pd.read_csv(options.filename,\n",
    "                       sep=sep_dict[options.delimiter],\n",
    "                       index_col = 0 if options.has_rownames else None,\n",
    "                       header = 'infer' if options.has_colnames else None)\n",
    "\n",
    "    # Read label if available\n",
    "    label = None\n",
    "    if options.group is not None:\n",
    "        label = pd.read_csv(options.group,\n",
    "                            sep=sep_dict[options.delimiter],\n",
    "                            index_col = 0 if options.group_rownames else None,\n",
    "                            header=\"infer\" if options.group_colnames else None)\n",
    "        label = label.iloc[:,0].values\n",
    "\n",
    "    # Perform dimensionality reduction\n",
    "    coords = dimred(X=data,\n",
    "                    label=label,\n",
    "                    scale=options.scale, \n",
    "                    methods=options.methods,\n",
    "                    tsne_perplexity=options.tsne_perplexity,\n",
    "                    tsne_angle=options.tsne_angle,\n",
    "                    umap_neighbors=options.umap_neighbors,\n",
    "                    umap_distance=options.umap_distance,\n",
    "                    umap_metric=options.umap_metric)\n",
    "\n",
    "    # Plot\n",
    "    dimred_plot(coordinates=coords, \n",
    "                plot_height=options.height, \n",
    "                plot_fontscale=options.font_scale, \n",
    "                plot_markersize=options.marker_size,\n",
    "                outfile=options.outfile)"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.6.6"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
