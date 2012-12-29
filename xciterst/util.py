import BeautifulSoup
import re
import xciterst

from docutils import nodes

def html2rst (html):
    """
    Transform html to reStructuredText internal representation.

    reStructuredText inline markup cannot be nested. The CSL processor
    does produce nested markup, so we ask the processor to deliver HTML,
    and use this function to convert it to the internal representation.
    It depends on Beautiful Soup.

    Note that the function supports small-caps, with the smallcaps
    node name. The Translator instance used by the Writer that consumes
    the output must be extended to support this node type.
    """
    def cleanString(str):
        """
        Replace HTML entities with character equivalents.

        Only these four characters are encoded as entities by the CSL
        processor when running in HTML mode.
        """
        str = str.replace("&#38;", "&")
        str = str.replace("&#60;", "<")
        str = str.replace("&#32;", ">")
        str = str.replace("&#160;", u"\u00A0")
        return str

    def is_empty_paragraph(node):
        if isinstance(node, nodes.paragraph):
            t = node.astext()
            return t == ' ' or t == ''
        else:
            return False

    def wrap_text(node_list):
        # in rst text must be wrapped in a paragraph, I believe
        # at least rst2pdf disappears the text if it is not - EGH
        retval = []
        last_was_text = False
        # group text nodes in paragraphs
        for node in node_list:
            if isinstance(node, nodes.Inline) or isinstance(node, nodes.Text):
                if last_was_text:
                    retval[-1] += node
                else:
                    retval.append(nodes.paragraph("","", node))
                    last_was_text = True
            else:
                retval.append(node)
                last_was_text = False
        return [ n for n in retval if not(is_empty_paragraph(n)) ]

    def compact(lst):
        return [ x for x in lst if (x is not None) ]

    def walk(html_node):
        """
        Walk the tree, building a reStructuredText object as we go.
        """
        if html_node is None:
            return None
        elif ((type(html_node) == BeautifulSoup.NavigableString) or (type(html_node) == str) or (type(html_node) == unicode)
):
            # Terminal nodes
            text = cleanString(unicode(html_node))
            # whitespace is significant in reST, so normalize empties to a single space
            if re.match("^\s+$", text):
                return nodes.Text(" ")
            else:
                return nodes.Text(text)
        else:
            # Nesting nodes.
            if (html_node.name == 'span'):
                ret = None
                if (html_node.has_key('style') and (html_node['style'] == "font-style:italic;")):
                    children = compact([walk(c) for c in html_node.contents])
                    return nodes.emphasis("", "", *children)
                elif (html_node.has_key('style') and (html_node['style'] == "font-variant:small-caps;")):
                    children = compact([walk(c) for c in html_node.contents])
                    return xciterst.smallcaps("", "", *children)
                elif (html_node.has_key('style') and (html_node['style'] == "font-style:normal;")):
                    children = compact([walk(c) for c in html_node.contents])
                    return nodes.emphasis("", "", *children)
                else:
                    children = compact(walk("".join([ str(c) for c in html_node.contents ])))
                    return nodes.generated("", "", *children)
            if (html_node.name == 'i'):
                children = compact([walk(c) for c in html_node.contents])
                return nodes.emphasis("", "", *children)
            elif (html_node.name == 'b'):
                children = compact([walk(c) for c in html_node.contents ])
                return nodes.strong("", "", *children)
            elif (html_node.name == 'p'):
                children = compact([ walk(c) for c in html_node.contents ])
                return nodes.paragraph("", "", *children)
            elif (html_node.name == 'a'):
                children = compact([ walk(c) for c in html_node.contents ])
                return apply(nodes.reference, ["", ""] + children, { 'refuri' : html_node['href'] })
            elif (html_node.name == 'div'):
                children = compact([ walk(c) for c in html_node.contents ])
                classes = re.split(" ", html_node.get('class', ""))
                return nodes.container("", *wrap_text(children), classes=classes)
    
    doc = BeautifulSoup.BeautifulSoup(html)
    ret = compact([ walk(c) for c in doc.contents ])
    return ret
