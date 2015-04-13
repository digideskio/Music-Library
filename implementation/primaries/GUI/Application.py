from PyQt4 import QtCore, QtGui
import sys, os, pickle, threading, queue
import time
from implementation.primaries.GUI import StartupWidget, thread_classes, MainWindow, PlaylistDialog, licensePopup, renderingErrorPopup, ImportDialog
from implementation.primaries.ExtractMetadata.classes import MusicManager, SearchProcessor
from implementation.primaries.Drawing.classes import LilypondRender, MxmlParser, Exceptions


class Application(object):

    def __init__(self, app):
        self.app = app
        self.previous_collections = []
        self.col_file = ".collections"
        self.getPreviousCollections()
        self.SaveCollections()
        self.manager = None
        self.main = None
        self.folder = ""
        self.theme = "dark"
        if len(self.previous_collections) == 0:
            self.startUp()
        else:
            self.folder = self.previous_collections[-1]
            self.setupMainWindow()

    def startUp(self):
        self.folder = ""
        self.startup = StartupWidget.Startup(self)
        self.startup.show()

    def removeCollection(self, folder):
        if os.path.exists(os.path.join(folder, "music.db")):
            os.remove(os.path.join(folder, "music.db"))
        self.previous_collections.remove(folder)
        self.SaveCollections()

    def getPreviousCollections(self):
        try:
            col_fob = open(self.col_file, 'rb')
        except:
            self.SaveCollections()
            col_fob = open(self.col_file, 'rb')
        result_temp = pickle.load(col_fob)
        if result_temp is not None:
            self.previous_collections = result_temp
        return self.previous_collections

    def SaveCollections(self):
        col_fob = open(self.col_file, 'wb')
        pickle_obj = pickle.Pickler(col_fob)
        pickle_obj.dump(self.previous_collections)

    def addFolderToCollectionList(self, name):
        if name not in self.previous_collections:
            self.previous_collections.append(name)

    def FolderFetched(self, foldername):
        self.folder = foldername
        if self.folder != "":
            self.addFolderToCollectionList(foldername)
            self.SaveCollections()
            self.startup.close()
            self.setupMainWindow()

    def setupMainWindow(self):
        self.manager = MusicManager.MusicManager(self, folder=self.folder)
        self.manager.runApiOperation()
        self.updateDb()
        self.main = MainWindow.MainWindow(self)
        self.main.show()

    def getPlaylistFileInfo(self, playlist):
        return self.manager.getPlaylistFileInfo(playlist)

    def getFileInfo(self, filename):
        file_info = self.manager.getFileInfo(filename)
        return file_info

    def loadUserPlaylistsForAGivenFile(self, filename):
        data = self.manager.getPlaylistByFilename(filename)
        return data

    def async_handle(self, data, method, callback, callback_data):
        thr = threading.Thread(target=method, args=data, kwargs={})
        thr.start() # will run "foo"
        while(thr.is_alive()):
            print("running")# will return whether foo is running currently
        thr.join() # will wait till "foo" is done
        callback(callback_data)


    def downloadFile(self, filename):
        async = thread_classes.Async_Handler((filename,), self.manager.downloadFile, self.main.loadPiece, filename)
        async.execute()

    def onRenderTaskFinished(self, errorList, filename=""):
        pdf = os.path.join(self.folder, filename)
        if not os.path.exists(pdf):
            errorList.append(
                "file rendering failed to produce a pdf, check above errors")
        if len(errorList) > 0:
            self.errorPopup(errorList)
        if os.path.exists(pdf):
            self.main.onPieceLoaded(pdf, filename)

    def loadFile(self, filename):
        '''
        This method should:
        - setup a renderer object
        - run it
        - return the pdf location
        :return: filename of generated pdf
        '''
        pdf_version = filename.split(".")[0] + ".pdf"
        if os.path.exists(os.path.join(self.folder, pdf_version)):
            return os.path.join(self.folder, pdf_version)
        else:
            if not os.path.exists(os.path.join(self.folder, filename)):
                license = self.manager.getLicense(filename)
                self.licensePopup = licensePopup.LicensePopup(self, license, filename, self.theme)
                self.licensePopup.setWindowFlags(QtCore.Qt.Dialog)
                self.licensePopup.exec()
            else:
                errorQueue = queue.Queue()
                async_renderer = thread_classes.Async_Handler_Queue(self.startRenderingTask,
                                                                    self.onRenderTaskFinished,
                                                                    errorQueue,
                                                                    (filename,),
                                                                    kwargs={"filename" : pdf_version})
                async_renderer.execute()


    def importPopup(self):
        dialog = ImportDialog.ImportDialog(self, self.theme)
        dialog.setWindowFlags(QtCore.Qt.Dialog)
        dialog.exec()

    def copyFiles(self, fnames):
        self.manager.copyFiles(fnames)
        self.updateDb()
        self.main.onSortMethodChange()
        self.main.loadPlaylists()

    def errorPopup(self, errors):
        popup = renderingErrorPopup.RenderingErrorPopup(
            self,
            errors,
            self.theme)
        popup.setWindowFlags(QtCore.Qt.Dialog)
        popup.exec()

    def onQueryComplete(self, data, online=False):
        query_results = {}
        if online:
            query_results["Online"] = data
        else:
            query_results["Offline"] = data
        self.main.onQueryReturned(query_results)

    def query(self, input):
        data = SearchProcessor.process(input)
        data_queue = queue.Queue()
        offline_handler = thread_classes.Async_Handler_Queue(self.manager.runQueries,
                                                             self.onQueryComplete,
                                                             data_queue, (data,))
        online_handler = thread_classes.Async_Handler_Queue(self.manager.runQueries,
                                                             self.onQueryComplete,
                                                             data_queue, (data,),
                                                             kwargs={"online":True})
        offline_handler.execute()
        online_handler.execute()

        self.query_results = {}


    def startRenderingTask(self, fname, filename=""):
        errorList = []
        parser = MxmlParser.MxmlParser()
        piece_obj = None
        try:
            piece_obj = parser.parse(os.path.join(self.folder, fname))
        except Exceptions.DrumNotImplementedException as e:
            errorList.append(
                "Drum tab found in piece: this application does not handle drum tab.")
        except Exceptions.TabNotImplementedException as e:
            errorList.append(
                "Guitar tab found in this piece: this application does not handle guitar tab.")

        if piece_obj is not None:
            try:
                loader = LilypondRender.LilypondRender(
                    piece_obj,
                    os.path.join(
                        self.folder,
                        fname))
                loader.run()
            except BaseException as e:
                errorList.append(str(e))
        return errorList

    def updateDb(self):
        self.manager.refresh()

    def makeNewCollection(self):
        self.main.close()
        self.startUp()

    def addPlaylist(self, data):
        self.manager.addPlaylist(data)

    def loadPieces(self, method="title"):
        summary_strings = self.manager.getPieceSummaryStrings(method)
        return summary_strings

    def getPlaylists(self, select_method="all"):
        results = self.manager.getPlaylists(select_method=select_method)
        return results

    def getCreatedPlaylists(self):
        results = self.manager.getPlaylistsFromPlaylistTable()
        return results

    def PlaylistPopup(self):
        popup = PlaylistDialog.PlaylistDialog(self, self.theme)
        popup.setWindowFlags(QtCore.Qt.Dialog)
        popup.exec()

    def removePlaylists(self, playlists):
        self.manager.deletePlaylists(playlists)

    def updatePlaylistTitle(self, new_title, old_title):
        self.manager.updatePlaylistTitle(new_title, old_title)

    def loadPlaylists(self):
        pass


def main():

    app = QtGui.QApplication(sys.argv)

    app_obj = Application(app)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
