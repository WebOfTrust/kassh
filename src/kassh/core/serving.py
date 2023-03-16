# -*- encoding: utf-8 -*-
"""
KASSH
kassh.core.serving module

Endpoint service
"""

import falcon
from hio.core import http
from keri import help
from keri.app import indirecting, storing
from keri.core import routing, eventing
from keri.end import ending
from keri.peer import exchanging
from keri.vdr import viring, verifying
from keri.vdr.eventing import Tevery

from kassh.core import handling, basing

logger = help.ogler.getLogger()


def setup(hby, *, alias, httpPort):
    """ Setup serving package and endpoints

    Parameters:
        hby (Habery): identifier database environment
        alias (str): alias of the identifier representing this agent
        httpPort (int): external port to listen on for HTTP messages

    """
    # make hab
    hab = hby.habByName(name=alias)
    if hab is None:
        hab = hby.makeHab(name=alias, transferable=True)

    print(f"Using hab {hab.name}:{hab.pre}")
    mbx = storing.Mailboxer(name=hby.name)
    reger = viring.Reger(name=hab.name, db=hab.db, temp=False)
    rep = storing.Respondant(hby=hby, mbx=mbx)
    verifier = verifying.Verifier(hby=hby, reger=reger)
    cdb = basing.CueBaser(name=hby.name)
    auther = handling.Authorizer(hby=hby, hab=hab, cdb=cdb, reger=reger)

    rvy = routing.Revery(db=hby.db)

    exc = exchanging.Exchanger(db=hby.db, handlers=[])
    handling.loadHandlers(exc=exc, hby=hby, cdb=cdb)

    kvy = eventing.Kevery(db=hby.db,
                          lax=True,
                          local=False,
                          rvy=rvy)
    kvy.registerReplyRoutes(router=rvy.rtr)

    tvy = Tevery(reger=verifier.reger,
                 db=hby.db,
                 local=False)
    tvy.registerReplyRoutes(router=rvy.rtr)

    app = falcon.App(
        middleware=falcon.CORSMiddleware(
            allow_origins='*',
            allow_credentials='*',
            expose_headers=['cesr-attachment', 'cesr-date', 'content-type']))

    server = http.Server(port=httpPort, app=app)
    httpServerDoer = http.ServerDoer(server=server)

    ending.loadEnds(app, hby=hby, default=hab.pre)

    doers = [httpServerDoer, auther, exc]
    mbd = indirecting.MailboxDirector(hby=hby,
                                      exc=exc,
                                      kvy=kvy,
                                      tvy=tvy,
                                      rvy=rvy,
                                      verifier=verifier,
                                      rep=rep,
                                      topics=["/receipt", "/replay", "/multisig", "/credential", "/delegate",
                                              "/challenge"])
    doers.append(mbd)

    return doers
