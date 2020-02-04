IBBS = ibbs$(shell date +%m%y)
IBBS_URL = https://www.telnetbbsguide.com/bbslist/$(IBBS).zip
BBSDB = bbsdb.sqlite
TIMEOUT = 20
MAXC = 100

HTMLDOCS = \
	   html/index.html \
	   html/up.html \
	   html/down.html

GENERATED = \
	    magiterm.ini \
	    qodem.ini \
	    ibbs.json

all: $(GENERATED)

html: $(HTMLDOCS)

clean:
	rm -f $(GENERATED) $(HTMLDOCS)

magiterm.ini: $(IBBS)/syncterm.lst
	ibbs sync2magi -i $< -o $@

qodem.ini: $(IBBS)/syncterm.lst
	ibbs sync2qodem -i $< -o $@

ibbs.json: $(IBBS)/syncterm.lst
	ibbs sync2json -i $< -o $@

$(IBBS).zip:
	curl -o $@ $(IBBS_URL)

$(IBBS): $(IBBS).zip
	unzip -d $@ $<

$(IBBS)/syncterm.lst: $(IBBS)

.lastcheck: $(IBBS)/syncterm.lst
	ibbs check -i $(IBBS)/syncterm.lst -d $(BBSDB) \
		-t $(TIMEOUT) -m $(MAXC) && touch .lastcheck

html/up.html: .lastcheck
	ibbs render -s up -o $@

html/down.html: .lastcheck
	ibbs render -s down -o $@

html/index.html: .lastcheck
	ibbs render -o $@
