
# coding: utf-8

# In[ ]:


#%matplotlib inline


# In[ ]:


from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import umap
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sys
from optparse import OptionParser, OptionGroup

parser = OptionParser()
parser.add_option("-f", "--file", 
                  dest="filename",
                  help="Matrix with observations as rows and variables as columns.",
                  action="store",
                  metavar="FILE")
parser.add_option("-d", "--delimiter",
                  dest="delimiter",
                  help="Delimiter to use. Options are 'tab', 'comma' or 'semicolon'. [default: %default]",
                  action="store",
                  choices=["tab", "comma", "semicolon"],
                  default="tab")
parser.add_option("-c",
                  action="store_true", 
                  dest="has_colnames",
                  help="Flag to indicate that the first row of the matrix is a header. [default: %default]",
                  default=True)
parser.add_option("-r", 
                  action="store_true", 
                  dest="has_rownames",
                  help="Flag to indicate that the first column of the matrix contains rownames. [default: %default]",
                  default=True)
parser.add_option("-m", "--methods",
                  dest="methods",
                  help="String specifying combination of dimensionality reduction methods to execute. 'P' for PCA, 'T' for tSNE, 'U' for UMAP. [default: %default]",
                  default="PTU",
                  metavar="COMBINATION")
parser.add_option("-g", "--group",
                  dest="group",
                  help="File containing a single column with no header to color the observations (in the same order).",
                  metavar="LABEL_FILE")
parser.add_option("--group_rownames",
                  action="store_true",
                  dest="group_rownames",
                  help="Flag to indicate that the label file has rownames. [default: %default]",
                  default=False)
parser.add_option("--group_header",
                  action="store_true",
                  dest="group_colnames",
                  help="Flag to indicate that the label file has a header. [default: %default]",
                  default=False)
parser.add_option("-o", "--outfile",
                  dest="outfile",
                  help="Path for output file in pdf format. [default: %default]",
                  metavar="OUTPUT_FILE",
                  default="out.pdf")

group = OptionGroup(parser, "Dimensionality reduction parameters")
group.add_option("-s", "--scale", 
                 action="store_true",
                 dest="scale",
                 help="Standardize data to zero mean and unit variance. [default: %default]",
                 default=False)
group.add_option("--tsne_perplexity",
                 action="store",
                 dest="tsne_perplexity",
                 help="Perplexity parameter for tSNE. [default: %default]",
                 default=30,
                 type="int")
group.add_option("--tsne_angle",
                 action="store",
                 dest="tsne_angle",
                 help="Angle parameter for tSNE. [default: %default]",
                 default=0.5,
                 type="float")
group.add_option("--umap_neighbors",
                 action="store",
                 dest="umap_neighbors",
                 help="Number of neighbors to use in UMAP. [default: %default]",
                 default=15,
                 type="int")
group.add_option("--umap_distance",
                 action="store",
                 dest="umap_distance",
                 help="Effective minimum distance between observations in UMAP. [default: %default]",
                 default=0.01,
                 type="float")
group.add_option("--umap_metric",
                 action="store",
                 dest="umap_metric",
                 help="Metric to use in UMAP. [default: %default]",
                 default="euclidean",
                 type="string")
parser.add_option_group(group)

group2 = OptionGroup(parser, "Graphical output parameters")
group2.add_option("--height", 
                 action="store",
                 dest="height",
                 help="Plot height in inches. Width is calculated so that each facet has an aspect ratio of 1 with respect to the height. [default: %default]",
                 default=8,
                 type="float")
group2.add_option("--font_scale",
                  action="store",
                  dest="font_scale",
                  help="Font scale (1=small, 5 = large). [default: %default]",
                  default=2,
                  type="float")
group2.add_option("--marker_size",
                  action="store",
                  dest="marker_size",
                  help="Marker size. [default: %default]",
                  default=50,
                  type="float")
parser.add_option_group(group2)


# In[ ]:


def dimred(X, label=None, scale=False, methods="PTU", tsne_perplexity=30, tsne_angle=0.5, umap_neighbors=15,
           umap_distance=0.01, umap_metric="euclidean"):
    
    methods = [x for x in methods]
    random_state=1
    
    if "P" in methods:
        pca_fit = PCA(n_components=2, random_state=random_state).fit_transform(X)
        pca_fit = pd.DataFrame(pca_fit, columns = ["X", "Y"])
        pca_fit["method"] = "PCA"
        pca_fit["label"] = pd.Series(label, index = pca_fit.index)
    else:
        pca_fit = None

    if "T" in methods:
        tsne_fit = TSNE(n_components=2, perplexity=tsne_perplexity, angle=tsne_angle, 
                        random_state=random_state).fit_transform(X)
        tsne_fit = pd.DataFrame(tsne_fit, columns=["X", "Y"])
        tsne_fit["method"] = "tSNE"
        tsne_fit["label"] = pd.Series(label, index = tsne_fit.index)
    else:
        tsne_fit = None

    if "U" in methods:
        umap_fit = umap.UMAP(n_neighbors=umap_neighbors, min_dist=umap_distance, 
                             metric=umap_metric, random_state=random_state).fit_transform(X)
        umap_fit = pd.DataFrame(umap_fit, columns=["X", "Y"])
        umap_fit["method"] = "UMAP"
        umap_fit["label"] = pd.Series(label, index = umap_fit.index)
    else:
        umap_fit = None

    final_df = pd.concat([pca_fit, tsne_fit, umap_fit], axis = 0)
    
    return(final_df)

def dimred_plot(coordinates, plot_height, plot_fontscale, plot_markersize, outfile):
    sns.set(font_scale=plot_fontscale)
    g = sns.FacetGrid(coordinates, col="method", sharex=False, sharey=False, hue="label", 
                      height = plot_height, aspect=1)
    g.map(plt.scatter, "X", "Y", alpha=.7, s = 50)
    g.add_legend()
    g.fig.savefig(outfile, bbox_inches="tight")


# In[ ]:


if __name__ == "__main__":
    #args = ["-f", "file.tsv", "-g", "y.tsv", "--group_rownames", "--group_header"]
    (options, args) = parser.parse_args()
    sep_dict = {"tab": "\t", "comma": ",", "semicolon":";"}

    # TODO: Do argument checking here
    if options.filename is None:
        parser.print_help()
        sys.exit(1)

    # Read input data
    data = pd.read_csv(options.filename,
                       sep=sep_dict[options.delimiter],
                       index_col = 0 if options.has_rownames else None,
                       header = 'infer' if options.has_colnames else None)

    # Read label if available
    label = None
    if options.group is not None:
        label = pd.read_csv(options.group,
                            sep=sep_dict[options.delimiter],
                            index_col = 0 if options.group_rownames else None,
                            header="infer" if options.group_colnames else None)
        label = label.iloc[:,0].values

    # Perform dimensionality reduction
    coords = dimred(X=data,
                    label=label,
                    scale=options.scale, 
                    methods=options.methods,
                    tsne_perplexity=options.tsne_perplexity,
                    tsne_angle=options.tsne_angle,
                    umap_neighbors=options.umap_neighbors,
                    umap_distance=options.umap_distance,
                    umap_metric=options.umap_metric)

    # Plot
    dimred_plot(coordinates=coords, 
                plot_height=options.height, 
                plot_fontscale=options.font_scale, 
                plot_markersize=options.marker_size,
                outfile=options.outfile)

