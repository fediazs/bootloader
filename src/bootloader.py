import os

from machine import SDCard

VERSION='1.0'
class Bootloader:
    
    def __init__(self):
        self.sd = SDCard()
        self.mount_point = "/sd"
        self.log_file_path = self.mount_point + "/update.txt"
        self.log_file = None
        self.backup_file = None
        self.do_update = False
        self._mount_sd()

    def _mount_sd(self):
        try:
            os.mount(self.sd, self.mount_point)
            print("SD card montada en", self.mount_point)
            
            files = os.listdir(self.mount_point)

            backup_path = self.mount_point + "/backup.txt"
            if "backup.txt" in files:
                self.backup_file = open(backup_path, "a")
                self.backup_file.write("\n--- Backup iniciado ---\n")
                self._backup_internal_files("/", self.mount_point + "/backup")
                self.backup_file.write("--- Backup finalizado ---\n")
                self.backup_file.close()
                os.rename(self.mount_point + "/backup.txt", self.mount_point + "/backup_done.txt")
                
            if "update.txt" in files:
                self.do_update = True
                self.log_file = open(self.log_file_path, "a")
                self.log_file.write("\n--- Copia iniciada ---\n")

        except Exception as e:
            print("Error al montar SD:", e)

    def _backup_file(self, src, dst):
        try:
            with open(src, 'rb') as fsrc:
                with open(dst, 'wb') as fdst:
                    while True:
                        buf = fsrc.read(512)
                        if not buf:
                            break
                        fdst.write(buf)
            print("Backup:", src, "→", dst)
            self._write_backup_log("Backup: " + src + " → " + dst)
        except Exception as e:
            print("Error en backup:", src, "→", e)
            self._write_backup_log("Error backup: " + src + " → " + str(e))

    def _backup_internal_files(self, src_dir, dst_dir):
        try:
            if not dst_dir in os.listdir(self.mount_point):
                try:
                    os.mkdir(dst_dir)
                except:
                    pass

            for entry in os.listdir(src_dir):
                if entry.startswith('.') or entry in ['sd', 'update.txt', 'backup.txt','update_done.txt', 'backup_done.txt']:
                    continue
                src_path = src_dir + "/" + entry
                dst_path = dst_dir + "/" + entry

                if os.stat(src_path)[0] & 0x4000:  # Es directorio
                    try:
                        os.mkdir(dst_path)
                    except:
                        pass
                    self._backup_internal_files(src_path, dst_path)
                else:
                    self._backup_file(src_path, dst_path)
        except Exception as e:
            print("Error en backup:", e)
            self._write_backup_log("Error en backup: " + str(e))


    def _write_backup_log(self, message):
        try:
            if self.backup_file:
                self.backup_file.write(message + "\n")
        except:
            pass

    def _umount_sd(self):
        try:
            if self.log_file:
                self.log_file.write("--- Copia finalizada ---\n")
                self.log_file.close()

            os.umount(self.mount_point)
        except Exception as e:
            print("Error al desmontar SD:", e)
        self.sd.deinit()

    def _write_log(self, message):
        try:
            if self.log_file:
                self.log_file.write(message + "\n")
        except Exception as e:
            print("Error escribiendo log:", e)

    def _copy_file(self, src, dst):
        with open(src, 'rb') as fsrc:
            with open(dst, 'wb') as fdst:
                while True:
                    buf = fsrc.read(512)
                    if not buf:
                        break
                    fdst.write(buf)
        print("Copiado:", src, "→", dst)
        self._write_log(f"Copiado: {src} → {dst}")

    def _recursive_copy(self, src_dir, dst_dir):
        try:
            for entry in os.listdir(src_dir):
                if src_dir == self.mount_point and entry == "backup":
                    # Excluir el directorio /sd/backup
                    continue
                 
                src_path = src_dir + "/" + entry
                dst_path = dst_dir + "/" + entry

                if os.stat(src_path)[0] & 0x4000:  # Es directorio
                    if not entry.startswith('.'):
                        try:
                            os.mkdir(dst_path)
                        except OSError:
                            pass  # Ya existe
                        self._recursive_copy(src_path, dst_path)
                else:
                    if entry.endswith('.py') or entry.endswith('.mpy') or entry.endswith('.json'):
                        self._copy_file(src_path, dst_path)
        except Exception as e:
            print("Error al copiar:", e)

    def run(self):
        if self.do_update:
            print("Iniciando copia desde SD...")
            self._recursive_copy(self.mount_point, "/")
            print("Copia finalizada.")
            os.rename(self.mount_point + "/update.txt", self.mount_point + "/update_done.txt")             
        self._umount_sd()

# Ejemplo de uso:
if __name__ == "__main__":
    bootloader = Bootloader()
    bootloader.run()
