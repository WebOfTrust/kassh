# -*- encoding: utf-8 -*-
"""
KASSH
kassh.core.handling module

EXN Message handling
"""
import datetime
import os
import pwd
import stat

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from hio.base import doing
from hio.help import decking
from keri.app import agenting
from keri.core import coring
from keri.help import helping

AUTH_SCHEMA_SAID = "EKgMCHV98k4xz2rJnt2x556pGBCUfA6n5x03mvQv5tPo"


def loadHandlers(hby, cdb, exc):
    """ Load handlers for the peer-to-peer challenge response protocol

    Parameters:
        hby (Habery): database environment
        cdb (CueBaser): communication escrow database environment
        exc (Exchanger): Peer-to-peer message router

    """
    proofs = PresentationProofHandler(hby=hby, cdb=cdb)
    exc.addHandler(proofs)


class PresentationProofHandler(doing.Doer):
    """ Processor for responding to presentation proof peer to peer message.

      The payload of the message is expected to have the following format:

    """

    resource = "/presentation"

    def __init__(self, hby, cdb, cues=None, **kwa):
        """ Initialize instance

        Parameters:
            hby (Habery): database environment
            cdb (CueBaser): communication escrow database environment
            cue(Deck): outbound cues
            **kwa (dict): keyword arguments passes to super Doer

        """
        self.msgs = decking.Deck()
        self.cues = cues if cues is not None else decking.Deck()
        self.hby = hby
        self.cdb = cdb

        super(PresentationProofHandler, self).__init__()

    def do(self, tymth, tock=0.0, **opts):
        """ Handle incoming messages by parsing and verifying the credential and storing it in the wallet

        Parameters:
            tymth (function): injected function wrapper closure returned by .tymen() of
                Tymist instance. Calling tymth() returns associated Tymist .tyme.
            tock (float): injected initial tock value

        Messages:
            payload is dict representing the body of a /credential/issue message
            pre is qb64 identifier prefix of sender
            sigers is list of Sigers representing the sigs on the /credential/issue message
            verfers is list of Verfers of the keys used to sign the message


        """
        self.wind(tymth)
        self.tock = tock
        yield self.tock

        while True:
            while self.msgs:
                msg = self.msgs.popleft()
                payload = msg["payload"]
                # TODO: limit presentations from issuee or issuer from flag.

                sender = payload["i"]
                said = payload["a"] if "a" in payload else payload["n"]

                print(f"Credential {said} presented from {sender}")

                prefixer = coring.Prefixer(qb64=sender)
                saider = coring.Saider(qb64=said)
                now = coring.Dater()

                self.cdb.snd.pin(keys=(saider.qb64,), val=prefixer)
                self.cdb.iss.pin(keys=(saider.qb64,), val=now)

                yield self.tock

            yield self.tock


class Authorizer(doing.DoDoer):
    """
    Authorizer is responsible for comminucating the receipt and successful verification
    of credential presentation and revocation messages from external third parties via
    web hook API calls.


    """

    TimeoutAuth = 600

    def __init__(self, hby, hab, cdb, reger):
        """

        Create a communicator capable of persistent processing of messages and performing
        web hook calls.

        Parameters:
            hby (Habery): identifier database environment
            hab (Hab): identifier environment of this Authorizer.  Used to sign hook calls
            cdb (CueBaser): communication escrow database environment
            reger (Reger): credential registry and database

        """
        self.hby = hby
        self.hab = hab
        self.cdb = cdb
        self.reger = reger
        self.witq = agenting.WitnessInquisitor(hby=hby)

        self.clients = dict()

        super(Authorizer, self).__init__(doers=[self.witq, doing.doify(self.escrowDo), doing.doify(self.monitorDo)])

    def processPresentations(self):

        for (said,), dater in self.cdb.iss.getItemIter():
            # cancel presentations that have been around longer than timeout
            now = helping.nowUTC()
            if now - dater.datetime > datetime.timedelta(seconds=self.TimeoutAuth):
                self.cdb.iss.rem(keys=(said,))
                print(f"removing {said}, it expired")
                continue

            if self.reger.saved.get(keys=(said,)) is not None:
                self.cdb.iss.rem(keys=(said,))
                creder = self.reger.creds.get(keys=(said,))
                if creder.schema != AUTH_SCHEMA_SAID:
                    print(f"invalid credential presentation, schema {creder.schema} does not match {AUTH_SCHEMA_SAID}")

                kever = self.hby.kevers[creder.subject["i"]]

                user = creder.subject["userName"]
                homeDir = os.path.join("/home", user)
                if os.path.exists(homeDir):
                    print(f"not creating user, {user} already exists.")

                cmd = f"useradd -p xxx -m {user}"
                if (err := os.system(cmd)) != 0:
                    print(f"unable to create user: {err}.")

                try:
                    ssh = os.path.join(homeDir, ".ssh")
                    os.mkdir(ssh)
                    authKeys = os.path.join(ssh, "authorized_keys")
                    f = open(authKeys, "w")
                    verkey = ed25519.Ed25519PublicKey.from_public_bytes(kever.verfers[0].raw)
                    pem = verkey.public_bytes(encoding=serialization.Encoding.OpenSSH,
                                              format=serialization.PublicFormat.OpenSSH)

                    for line in pem.splitlines(keepends=True):
                        f.write(line.decode("utf-8"))

                    f.close()
                    uid, gid = pwd.getpwnam(user).pw_uid, pwd.getpwnam(user).pw_gid
                    os.chown(ssh, uid, gid)
                    os.chown(authKeys, uid, gid)
                    os.chmod(ssh, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
                    os.chmod(authKeys, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)

                    self.cdb.accts.pin(keys=(creder.said,), val=(kever.prefixer, kever.sner))

                except (FileExistsError, FileNotFoundError) as e:
                    print(f"error creating SSH directory and files: {e}")

    def processRevocations(self):

        for (said,), dater in self.cdb.rev.getItemIter():

            # cancel revocations that have been around longer than timeout
            now = helping.nowUTC()
            if now - dater.datetime > datetime.timedelta(seconds=self.TimeoutAuth):
                self.cdb.rev.rem(keys=(said,))
                continue

            creder = self.reger.ccrd.get(keys=(said,))
            if creder is None:  # received revocation before credential.  probably an error but let it timeout
                continue

            regk = creder.status
            state = self.reger.tevers[regk].vcState(creder.said)
            if state is None:  # received revocation before status.  probably an error but let it timeout
                continue

            elif state.ked['et'] in (coring.Ilks.iss, coring.Ilks.bis):  # haven't received revocation event yet
                continue

            elif state.ked['et'] in (coring.Ilks.rev, coring.Ilks.brv):  # revoked
                self.cdb.rev.rem(keys=(said,))
                self.cdb.revk.pin(keys=(said, dater.qb64), val=creder)

    def escrowDo(self, tymth, tock=1.0):
        """ Process escrows of comms pipeline

        Steps involve:
           1. Sending local event with sig to other participants
           2. Waiting for signature threshold to be met.
           3. If elected and delegated identifier, send complete event to delegator
           4. If delegated, wait for delegator's anchor
           5. If elected, send event to witnesses and collect receipts.
           6. Otherwise, wait for fully receipted event

        Parameters:
            tymth (function): injected function wrapper closure returned by .tymen() of
                Tymist instance. Calling tymth() returns associated Tymist .tyme.
            tock (float): injected initial tock value.  Default to 1.0 to slow down processing

        """
        # enter context
        self.wind(tymth)
        self.tock = tock
        _ = (yield self.tock)

        while True:
            try:
                self.processEscrows()
            except Exception as e:
                print(e)

            yield 0.5

    def monitorDo(self, tymth, tock=1.0):
        """ Process active account AIDs to update on rotations

        Parameters:
            tymth (function): injected function wrapper closure returned by .tymen() of
                Tymist instance. Calling tymth() returns associated Tymist .tyme.
            tock (float): injected initial tock value.  Default to 1.0 to slow down processing

        """
        # enter context
        self.wind(tymth)
        self.tock = tock
        _ = (yield self.tock)

        while True:
            for (said,), (prefixer, seqner) in self.cdb.accts.getItemIter():
                self.witq.query(src=self.hab.pre, pre=prefixer.qb64)

                kever = self.hby.kevers[prefixer.qb64]
                if kever.sner.num > seqner.num:
                    print("Processing rotation...")
                    creder = self.reger.creds.get(keys=(said,))
                    user = creder.subject["userName"]
                    authKeys = os.path.join("/home", user, ".ssh", "authorized_keys")
                    f = open(authKeys, "w")
                    verkey = ed25519.Ed25519PublicKey.from_public_bytes(kever.verfers[0].raw)
                    pem = verkey.public_bytes(encoding=serialization.Encoding.OpenSSH,
                                              format=serialization.PublicFormat.OpenSSH)

                    for line in pem.splitlines(keepends=True):
                        f.write(line.decode("utf-8"))

                    f.close()
                    print(f"new key written to {authKeys}")

                    self.cdb.accts.pin(keys=(creder.said,), val=(kever.prefixer, kever.sner))
                yield 1.0

            yield 5.0

    def processEscrows(self):
        """
        Process credental presentation pipelines

        """
        self.processPresentations()
        self.processRevocations()
