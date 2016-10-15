import os,sys,requests
from functools import partial

def get_file(url, dest):
    sess = requests.Session()
    resp = sess.get(url, stream=True, timeout=10.)
    total = int(resp.headers['content-length'])
    downloaded = 0
    chunk_size=4096
    print("%s / %d" % (dest, total) )
    with open(dest, 'wb') as output:
        for chunk in resp.iter_content(chunk_size=chunk_size):
            if chunk:
                output.write(chunk)
                downloaded+=len(chunk)
                print "%s %d" % (dest, downloaded)
    return dest

def organize(inp_file, out_file, split_size=1, entries_num=None):
    assert inp_file
    assert out_file
    count = 0
    with open(inp_file, 'r') as inp_hand:
        with open(out_file, 'w') as out_hand:
            for line in inp_hand.readlines():
                params = line.replace('\n','').split(',')[::split_size]
                label = int(params[0])
                arr = ["0"] * 10
                arr[label] = "1"
                del params[0]
                print "resp size", len(params), len(arr)
                out_hand.write(",".join(params + arr) + '\n')
                if entries_num and (++count > entries_num):
                    break

def convert(images_str, labels_str, output_str, n=None):
    with open(images_str,'rb') as img_hand, open(labels_str,'rb') as lab_hand, open(output_str,'w') as out_hand:
        img_hand.read(16)
        lab_hand.read(8)
        #images = []
        count = 0
        for lrd in iter(partial(lab_hand.read, 1),''):
            image = []
            l = str(ord(lrd))
            count += 1
            image.append(l)
            for _ in range(28*28):
                image.append(str(ord(img_hand.read(1))))
            if n != None and count > n:
                break
            line = ",".join(image) + '\n'
            out_hand.write(line)
            if count % 1000 == 0:
                print count

def gunzip_it(i,o):
    import gzip
    print "gunzip %s -> %s" % (i,o)
    with gzip.open(i,'rb') as inf, open(o,'wb') as otf:
        otf.write(inf.read())


print "test database"
test_images_gz  = 't10k-images-idx3-ubyte.gz'
test_images     = 't10k-images-idx3-ubyte'
test_labels_gz  = 't10k-labels-idx1-ubyte.gz'
test_labels     = 't10k-labels-idx1-ubyte'

if not os.path.isfile(test_images_gz):
        get_file('http://yann.lecun.com/exdb/mnist/t10k-images-idx3-ubyte.gz',test_images_gz)
        gunzip_it(test_images_gz, test_images)


if not os.path.isfile(test_labels_gz):
        get_file('http://yann.lecun.com/exdb/mnist/t10k-labels-idx1-ubyte.gz',test_labels_gz)
        gunzip_it(test_labels_gz, test_labels)

convert(test_images, test_labels, "mnist_test.csv",10000)
organize('mnist_test.csv','test.csv',1)

print "train database"
train_images_gz = 'train-images-idx3-ubyte.gz'
train_images    = 'train-images-idx3-ubyte'
train_labels_gz = 'train-labels-idx1-ubyte.gz'
train_labels    = 'train-labels-idx1-ubyte'

if not os.path.isfile(train_images_gz):
        get_file('http://yann.lecun.com/exdb/mnist/train-images-idx3-ubyte.gz',train_images_gz)
        gunzip_it(train_images_gz, train_images)
if not os.path.isfile(train_labels_gz):
        get_file('http://yann.lecun.com/exdb/mnist/train-labels-idx1-ubyte.gz',train_labels_gz)
        gunzip_it(train_labels_gz, train_labels)

convert(train_images, train_labels, "mnist_train.csv")
organize('mnist_train.csv','train.csv',1)
