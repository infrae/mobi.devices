from xml.sax import make_parser
from xml.sax.handler import ContentHandler


def build_index_tree(wurfl_xml_stream, capabilities=None):
    from index.suffixtree import Node
    parser = make_parser()
    ch = WURFLContentHandler()
    if capabilities is not None:
        ch.capabilities = capabilities
    parser.setContentHandler(ch)
    parser.parse(sys.stdin)

    suffix_tree = Node('Root')
    for id, device in ch.devices.iteritems():
        suffix_tree.add(device.user_agent, value=device)
    return suffix_tree


class Device(object):
    """ A wurfl device object
    """
    def __init__(self, user_agent, parent=None):
        self.parent = parent
        self.user_agent = user_agent
        self.capabilities = {}

    def get_capability(self, name):
        if name in self.capabilities:
            return self.capabilities[name]
        if self.parent:
            return self.parent.get_capability(name)
        return None

    def __repr__(self):
        return '<%s.Device user_agent="%s">' % (__name__, self.user_agent)


class WURFLContentHandler(ContentHandler):

    devices = {}
    device = None
    capabilities = ['xhtml_support_level']

    def startElement(self, element, attrs):
        if element == 'device':
            self.device = self._build_device(element, attrs)
            self.devices[attrs['id']] = self.device
        if element == 'capability' and self.device:
            if attrs['name'] in self.capabilities:
                self.device.capabilities[attrs['name']] = attrs['value']

    def endElement(self, element):
        if element == 'device':
            self.device = None

    def _build_device(self, element, attrs):
        parent = self.devices.get(attrs['fall_back'])
        device = Device(attrs['user_agent'], parent=parent)
        return device


if __name__ == '__main__':
    import sys
    import cPickle
    import gzip
    file = gzip.open('index.pyk', 'wb')
    try:
        st = build_index_tree(sys.stdin)
        pickler = cPickle.Pickler(file)
        pickler.dump(st)
    finally:
        file.close()
