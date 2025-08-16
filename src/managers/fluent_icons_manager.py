"""Fixed broken docstring"""
"""Fixed broken docstring"""
print(f"Error: {e}")
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL not available - using emoji fallback only")

try:
    pass
except Exception as e:
    print(f"Error: {e}")
    import customtkinter as ctk
    CUSTOMTKINTER_AVAILABLE = True
except ImportError:
    CUSTOMTKINTER_AVAILABLE = False
    logging.warning("CustomTkinter not available - using standard Tkinter")

class EnhancedFluentIconManager:
    """Fixed broken docstring"""
    """Fixed broken docstring"""
        """Fixed broken docstring"""
        """Fixed broken docstring"""
            print(f"Error: {e}")
            from memory_optimization import get_icon_cache
            self.icon_cache = get_icon_cache()
            self.image_cache = get_icon_cache()  # Use same cache for both
        except ImportError:
            # Fallback to regular dict if memory_optimization not available
            self.icon_cache: Dict[str, Any] = {}
            self.image_cache: Dict[str, ImageTk.PhotoImage] = {}
        
        self.current_theme = 'light'
        self.custom_icons = {}
        self.default_icon_size = (16, 16)
        
        # Icon-Pfade definieren (Priorität von oben nach unten)
        # icons/ zuerst, da assets/icons/ beschädigte Dateien enthält
        self.icon_paths = [
            os.path.join(self.workspace_path, 'icons')
            os.path.join(self.workspace_path, 'assets')
            os.path.join(self.workspace_path, 'assets', 'icons')
        ]
        
        # Verfügbare lokale Icons scannen
        self.available_local_icons = self._scan_local_icons()
        
        # Custom Icons aus gespeicherten Einstellungen laden
        self._load_custom_icons()
        
        logging.info(f"Enhanced FluentIconManager initialisiert mit Workspace: {self.workspace_path}")
        logging.debug(f"Icon-Pfade: {self.icon_paths}")
        logging.debug(f"Verfügbare lokale Icons: {len(self.available_local_icons)}")

    def _scan_local_icons(self) -> Dict[str, str]:
        """Fixed broken docstring"""
        """Fixed broken docstring"""
                print(f"Error: {e}")
                for file in os.listdir(icon_path):
                    file_path = os.path.join(icon_path, file)
                    if os.path.isfile(file_path):
                        name, ext = os.path.splitext(file)
                        if ext.lower() in supported_extensions:
                            # Überprüfe Dateigröße - überspringe leere Dateien
                            file_size = os.path.getsize(file_path)
                            if file_size > 100:  # Mindestens 100 Bytes
                                # Verschiedene Namensformen speichern
                                available_icons[name.lower()] = file_path
                                available_icons[name.lower().replace('-', '_')] = file_path
                                available_icons[name.lower().replace('_', '-')] = file_path
                            else:
                                logging.debug(f"Überspringe leere Icon-Datei: {file_path} ({file_size} Bytes)")
                            
            except Exception as e:
                logging.warning(f"Fehler beim Scannen von {icon_path}: {e}")
        
        logging.debug(f"Gescannte Icons: {list(available_icons.keys()}")
        return available_icons

    def _find_local_icon(self, icon_name: str) -> Optional[str]:
        """Fixed broken docstring"""
        """Fixed broken docstring"""
            print(f"Error: {e}")
            from ui_theme import UITheme
            improved_name = UITheme.get_improved_icon_name(icon_name)
            if improved_name != icon_name:
                search_names.extend([)
                    improved_name.lower()
                    improved_name.lower().replace('_', '-')
                    improved_name.lower().replace('-', '_')
                ])
        except (ImportError, AttributeError):
            pass
        
        # Auch nach lokalem Mapping suchen
        if icon_name in self.LOCAL_ICON_MAPPING:
            mapped_name = self.LOCAL_ICON_MAPPING[icon_name]
            search_names.extend([)
                mapped_name.lower()
                mapped_name.lower().replace('_', '-')
                mapped_name.lower().replace('-', '_')
            ])
        
        for search_name in search_names:
            if search_name in self.available_local_icons:
                return self.available_local_icons[search_name]
        
        return None

    def load_png_icon(self, icon_filename: str, size: Tuple[int, int] = (20, 20) -> Optional[ImageTk.PhotoImage]:
        """Fixed broken docstring"""
        """Fixed broken docstring"""
                logging.error("❌ PIL/Pillow nicht verfügbar - kann PNG-Icons nicht laden")
            logging.warning("PIL/Pillow nicht verfügbar - kann PNG-Icons nicht laden")
            return None
        
        if debug_enabled:
            logging.info(f"🖼️ load_png_icon aufgerufen: filename='{icon_filename}', size={size}")
        
        # Cache-Key für Performance
        cache_key = f"{icon_filename}_{size}"
        cached_icon = self.image_cache.get(cache_key) if hasattr(self.image_cache, 'get') else self.image_cache.get(cache_key, None)
        if cached_icon:
            if debug_enabled:
                logging.info(f"✅ PNG-Icon aus Cache geladen: {icon_filename}")
            logging.debug(f"Icon aus Cache geladen: {icon_filename}")
            return cached_icon
        
        if debug_enabled:
            logging.info(f"🔍 Cache-Miss für PNG-Icon: {icon_filename}")
        
        # Dynamische Pfad-Suche: Durchsuche alle konfigurierten icon_paths
        icon_path = None
        for search_path in self.icon_paths:
            potential_path = os.path.join(search_path, icon_filename)
            if debug_enabled:
                logging.info(f"🔍 Prüfe Pfad: {potential_path}")
            
            if os.path.exists(potential_path):
                icon_path = potential_path
                if debug_enabled:
                    logging.info(f"✅ Icon gefunden in Pfad: {search_path}")
                logging.debug(f"Icon gefunden in Pfad: {search_path}")
                break
            else:
                if debug_enabled:
                    logging.info(f"❌ Icon nicht gefunden in: {potential_path}")
        
        # Wenn Icon in keinem Pfad gefunden wurde
        if not icon_path:
            if debug_enabled:
                logging.error(f"❌ Icon '{icon_filename}' wurde in KEINEM der konfigurierten Pfade gefunden!")
                logging.error(f"🔧 Konfigurierte Pfade: {self.icon_paths}")
                # Zeige verfügbare Dateien in den Pfaden
                for search_path in self.icon_paths:
                    if os.path.exists(search_path):
                        files = [f for f in os.listdir(search_path) if f.endswith(('.png', '.jpg', '.jpeg')][:5]
                        logging.error(f"📁 Verfügbare Dateien in {search_path}: {files}")
            logging.warning(f"Icon '{icon_filename}' wurde in keinem der konfigurierten Pfade gefunden: {self.icon_paths}")
            return None
        
        try:
            pass
        except Exception as e:
            print(f"Error: {e}")
            # Prüfe Dateigröße (mindestens 50 Bytes für valide PNG)
            file_size = os.path.getsize(icon_path)
            if file_size < 50:
                if debug_enabled:
                    logging.error(f"❌ Icon-Datei zu klein: '{icon_filename}' ({file_size} Bytes)")
                logging.warning(f"Icon-Datei '{icon_filename}' ist zu klein oder leer ({file_size} Bytes) - möglicherweise beschädigt")
                return None
            
            if debug_enabled:
                logging.info(f"✅ Dateigröße OK: {file_size} Bytes")
            
            # Sicherstellen, dass ein Root-Window existiert für PhotoImage
            import tkinter as tk
            if not hasattr(tk, '_default_root') or tk._default_root is None:
                temp_root = tk.Tk()
                temp_root.withdraw()
                if debug_enabled:
                    logging.info("🔧 Temporäres Root-Window erstellt")
            
            if debug_enabled:
                logging.info(f"🔄 Lade PNG-Datei: {icon_path}")
            
            # PNG-Datei sicher laden mit with-Statement
            with Image.open(icon_path) as img:
                if debug_enabled:
                    logging.info(f"📸 PNG geladen: {img.size}, Modus: {img.mode}")
                
                # Konvertiere explizit zu RGBA für bessere Kompatibilität
                img_rgba = img.convert("RGBA")
                if debug_enabled:
                    logging.info(f"🎨 RGBA-Konvertierung abgeschlossen")
                
                # Resize mit hochwertigem Resampling
                if img_rgba.size != size:
                    if debug_enabled:
                        logging.info(f"📏 Skaliere PNG: {img_rgba.size} -> {size}")
                    img_resized = img_rgba.resize(size, Image.Resampling.LANCZOS)
                else:
                    img_resized = img_rgba
                    if debug_enabled:
                        logging.info(f"✅ PNG-Größe bereits korrekt: {size}")
                
                # Konvertiere zu PhotoImage oder CTkImage
                if debug_enabled:
                    logging.info("🔄 Konvertiere PNG zu Image...")
                
                # CTkImage erstellen für bessere CustomTkinter-Kompatibilität
                if CUSTOMTKINTER_AVAILABLE:
                    try:
                        pass
                    except Exception as e:
                        print(f"Error: {e}")
                        ctk_image = ctk.CTkImage(light_image=img_resized, size=size)  # ✅ NUR light_image
                        
                        # In Cache speichern
                        if hasattr(self.image_cache, 'put'):
                            self.image_cache.put(cache_key, ctk_image)
                        else:
                            self.image_cache[cache_key] = ctk_image
                        
                        if debug_enabled:
                            logging.info(f"✅ CTkImage erfolgreich erstellt: {icon_filename}")
                        logging.info(f"Icon '{icon_filename}' erfolgreich geladen und skaliert von {img.size} auf {size}")
                        return ctk_image
                    except Exception as ctk_error:
                        if debug_enabled:
                            logging.warning(f"⚠️ CTkImage-Erstellung fehlgeschlagen, nutze PhotoImage: {ctk_error}")
                
                # Fallback zu PhotoImage
                photo = ImageTk.PhotoImage(img_resized)
                
                # In Cache speichern
                if hasattr(self.image_cache, 'put'):
                    self.image_cache.put(cache_key, photo)
                else:
                    self.image_cache[cache_key] = photo
                
                if debug_enabled:
                    logging.info(f"✅ PhotoImage erfolgreich erstellt: {icon_filename}")
                logging.info(f"Icon '{icon_filename}' erfolgreich geladen und skaliert von {img.size} auf {size}")
                return photo
                
        except FileNotFoundError:
            if debug_enabled:
                logging.error(f"❌ PNG-Datei nicht gefunden: {icon_path}")
            logging.error(f"Icon-Datei nicht gefunden: '{icon_filename}' in {icon_path}")
        except Image.UnidentifiedImageError:
            if debug_enabled:
                logging.error(f"❌ PNG nicht identifizierbar: {icon_path}")
            logging.error(f"Kann Icon-Datei nicht als Bild identifizieren: '{icon_filename}' - Datei möglicherweise beschädigt")
        except PermissionError:
            if debug_enabled:
                logging.error(f"❌ Keine Berechtigung für PNG: {icon_path}")
            logging.error(f"Keine Berechtigung zum Lesen der Icon-Datei: '{icon_filename}' in {icon_path}")
        except Exception as e:
            if debug_enabled:
                logging.error(f"❌ Unerwarteter PNG-Fehler: {icon_path} -> {str(e)}")
            logging.error(f"Unerwarteter Fehler beim Laden von Icon '{icon_filename}': {e}")
        
        return None

    def _load_image_icon(self, icon_path: str, size: Tuple[int, int] = None) -> Union[ctk.CTkImage, ImageTk.PhotoImage, None]:
        """Fixed broken docstring"""
        """Fixed broken docstring"""
                logging.error("❌ PIL/Pillow nicht verfügbar - kann keine Icons laden")
            return None
        
        if debug_enabled:
            logging.info(f"🖼️ _load_image_icon aufgerufen: path='{icon_path}', size={size}")
        
        # Extrahiere Dateinamen aus Pfad
        icon_filename = os.path.basename(icon_path)
        target_size = size or self.default_icon_size
        
        if debug_enabled:
            logging.info(f"📏 Zielgröße: {target_size}, Dateiname: {icon_filename}")
        
        # Wenn der Pfad bereits in assets/icons ist, nutze load_png_icon direkt
        if 'assets' in icon_path and 'icons' in icon_path:
            if debug_enabled:
                logging.info(f"♻️ Verwende load_png_icon für assets-Pfad: {icon_path}")
            return self.load_png_icon(icon_filename, target_size)
        
        # Für andere Pfade: Fallback zur alten Logik aber mit robusteren Checks
        cache_key = f"{icon_path}_{target_size}"
        
        cached_icon = self.image_cache.get(cache_key) if hasattr(self.image_cache, 'get') else self.image_cache.get(cache_key, None)
        if cached_icon:
            if debug_enabled:
                logging.info(f"✅ Icon aus Image-Cache geladen: {icon_path}")
            return cached_icon
        
        try:
            pass
        except Exception as e:
            print(f"Error: {e}")
            if not os.path.exists(icon_path):
                if debug_enabled:
                    logging.error(f"❌ Icon-Datei nicht gefunden: {icon_path}")
                print(f"[ICON_LOAD ERROR] Icon-Datei nicht gefunden: {icon_path}")
                return None
            
            # Überprüfe Dateigröße
            file_size = os.path.getsize(icon_path)
            if file_size < 50:  # Reduziert von 100 auf 50 Bytes
                if debug_enabled:
                    logging.error(f"❌ Icon-Datei zu klein: {icon_path} ({file_size} Bytes)")
                print(f"[ICON_LOAD ERROR] Icon-Datei zu klein oder leer: {icon_path} ({file_size} Bytes)")
                return None
            
            if debug_enabled:
                logging.info(f"✅ Icon-Datei OK: {icon_path} ({file_size} Bytes)")
            
            # Sicherstellen, dass ein Root-Window existiert
            import tkinter as tk
            if not hasattr(tk, '_default_root') or tk._default_root is None:
                temp_root = tk.Tk()
                temp_root.withdraw()
                if debug_enabled:
                    logging.info("🔧 Temporäres Root-Window erstellt")
                
            # Bild sicher laden mit with-Statement
            if debug_enabled:
                logging.info(f"🔄 Lade Bild: {icon_path}")
            
            with Image.open(icon_path) as img:
                if debug_enabled:
                    logging.info(f"📸 Bild geladen: {img.size}, Modus: {img.mode}")
                
                # Explizite RGBA-Konvertierung
                img_rgba = img.convert("RGBA")
                if debug_enabled:
                    logging.info(f"🎨 RGBA-Konvertierung abgeschlossen: {img_rgba.size}")
                
                # Größe anpassen
                if img_rgba.size != target_size:
                    if debug_enabled:
                        logging.info(f"📏 Größe anpassen: {img_rgba.size} -> {target_size}")
                    img_resized = img_rgba.resize(target_size, Image.Resampling.LANCZOS)
                else:
                    img_resized = img_rgba
                    if debug_enabled:
                        logging.info(f"✅ Größe bereits korrekt: {target_size}")
                
                # Konvertiere zu PhotoImage oder CTkImage
                if debug_enabled:
                    logging.info("🔄 Konvertiere Bild zu Image...")
                
                # CTkImage erstellen für bessere CustomTkinter-Kompatibilität
                if CUSTOMTKINTER_AVAILABLE:
                    try:
                        pass
                    except Exception as e:
                        print(f"Error: {e}")
                        # Use target_size instead of size parameter that might be None
                        ctk_image = ctk.CTkImage(light_image=img_resized, size=target_size)  # ✅ NUR light_image
                        
                        # In Cache speichern
                        if hasattr(self.image_cache, 'put'):
                            self.image_cache.put(cache_key, ctk_image)
                        else:
                            self.image_cache[cache_key] = ctk_image
                        
                        if debug_enabled:
                            logging.info(f"✅ CTkImage erfolgreich erstellt: {icon_path}")
                        print(f"[ICON_LOAD SUCCESS] Icon geladen: {icon_path} -> {target_size}")
                        return ctk_image
                    except Exception as ctk_error:
                        if debug_enabled:
                            logging.warning(f"⚠️ CTkImage-Erstellung fehlgeschlagen, nutze PhotoImage: {ctk_error}")
                        print(f"[ICON_LOAD ERROR] CTkImage creation failed: {ctk_error}")
                
                # Fallback zu PhotoImage
                photo = ImageTk.PhotoImage(img_resized)
                
                # In Cache speichern
                self.image_cache[cache_key] = photo
                
                if debug_enabled:
                    logging.info(f"✅ PhotoImage erfolgreich erstellt: {icon_path}")
                print(f"[ICON_LOAD SUCCESS] Icon geladen: {icon_path} -> {target_size}")
                return photo
                
        except Exception as e:
            if debug_enabled:
                logging.error(f"❌ Fehler beim Laden von Icon {icon_path}: {str(e)}")
            print(f"[ICON_LOAD ERROR] Fehler beim Laden von Icon {icon_path}: {e}")
            return None

    def "" -> Union[str, ctk.CTkImage, ImageTk.PhotoImage, None]:
        """Fixed broken docstring"""
        """Fixed broken docstring"""
            logging.info(f"📍 get_icon() aufgerufen: size={size}, fallback_to_emoji={fallback_to_emoji}")
        
        # Cache-Key erstellen
        cache_key = f"{icon_name}_{size or self.default_icon_size}_{self.current_theme}"
        
        if cache_key in self.icon_cache:
            if debug_enabled:
                logging.info(f"✅ Icon aus Cache geladen: {icon_name} (Cache-Key: {cache_key})")
            return self.icon_cache[cache_key]
        
        if debug_enabled:
            logging.info(f"🔍 Cache-Miss für {icon_name}, suche Icon...")
        
        result = None
        search_path_used = None
        
        # 1. Zuerst nach Custom Icons suchen
        if icon_name in self.custom_icons:
            custom_path = self.custom_icons[icon_name]
            if debug_enabled:
                logging.info(f"🔧 Custom Icon-Pfad gefunden: {icon_name} -> {custom_path}")
            
            if os.path.exists(custom_path):
                if debug_enabled:
                    logging.info(f"✅ Custom Icon-Datei existiert: {custom_path}")
                result = self._load_image_icon(custom_path, size)
                if result:
                    search_path_used = f"Custom: {custom_path}"
                    if debug_enabled:
                        logging.info(f"✅ Custom Icon erfolgreich geladen: {icon_name}")
                else:
                    if debug_enabled:
                        logging.warning(f"❌ Custom Icon konnte nicht geladen werden: {custom_path}")
            else:
                if debug_enabled:
                    logging.warning(f"❌ Custom Icon-Datei existiert nicht: {custom_path}")
        
        # 2. Dann nach lokalen Icons suchen
        if not result:
            if debug_enabled:
                logging.info(f"🔍 Suche lokales Icon für: {icon_name}")
            
            local_path = self._find_local_icon(icon_name)
            if local_path:
                if debug_enabled:
                    logging.info(f"📁 Lokaler Icon-Pfad gefunden: {icon_name} -> {local_path}")
                
                if os.path.exists(local_path):
                    if debug_enabled:
                        logging.info(f"✅ Lokale Icon-Datei existiert: {local_path}")
                    result = self._load_image_icon(local_path, size)
                    if result:
                        search_path_used = f"Local: {local_path}"
                        if debug_enabled:
                            logging.info(f"✅ Lokales Icon erfolgreich geladen: {icon_name}")
                    else:
                        if debug_enabled:
                            logging.warning(f"❌ Lokales Icon konnte nicht geladen werden: {local_path}")
                else:
                    if debug_enabled:
                        logging.warning(f"❌ Lokale Icon-Datei existiert nicht: {local_path}")
            else:
                if debug_enabled:
                    logging.info(f"❌ Kein lokaler Icon-Pfad gefunden für: {icon_name}")
                    # Verfügbare Icons auflisten
                    available_icons = list(self.available_local_icons.keys()[:10]  # Erste 10
                    logging.info(f"📋 Verfügbare lokale Icons (Beispiele): {available_icons}")
        
        # 3. Emoji-Fallback verwenden (nur für Nicht-CTkButton-Verwendung)
        if not result and fallback_to_emoji:
            if debug_enabled:
                logging.info(f"🔄 Prüfe Emoji-Fallback für: {icon_name}")
            
            # Emoji-Fallback nur für Labels verwenden, nicht für CTkButtons
            # CTkButtons können nicht mit Emoji-Strings umgehen
            if icon_name in self.FLUENT_ICONS:
                # Rückgabe None für CTkButton-Kompatibilität
                # Emoji-Fallback wird in der aufrufenden Methode behandelt
                result = None  # Nicht das Emoji zurückgeben
                if debug_enabled:
                    logging.info(f"😀 Emoji-Fallback verfügbar aber übersprungen für CTkButton: {icon_name}")
            else:
                if debug_enabled:
                    logging.warning(f"❌ Kein Emoji-Fallback verfügbar für: {icon_name}")
                    # Verfügbare Emojis auflisten
                    available_emojis = list(self.FLUENT_ICONS.keys()[:10]  # Erste 10
                    logging.info(f"📋 Verfügbare Emojis (Beispiele): {available_emojis}")
        
        # Cache speichern
        if result:
            self.icon_cache[cache_key] = result
            if debug_enabled:
                logging.info(f"💾 Icon in Cache gespeichert: {icon_name} (Key: {cache_key}, Quelle: {search_path_used})")
        else:
            if debug_enabled:
                logging.error(f"❌ KEIN ICON GEFUNDEN für: {icon_name}")
                logging.info(f"🔧 Verfügbare Suchpfade: {self.icon_paths}")
                logging.info(f"🔧 Custom Icons: {list(self.custom_icons.keys()}")
                logging.info(f"🔧 Cache-Status: {len(self.icon_cache)} Einträge")
        
        return result

    def get_icon_for_button(self, icon_name: str, size: Tuple[int, int] = (16, 16) -> Union[str, ImageTk.PhotoImage]:
        """Fixed broken docstring"""
        """Fixed broken docstring"""
        icon = self.""
        
        # Fallback auf generisches Icon
        if not icon:
            icon = self.""
        
        # Letzter Fallback
        if not icon:
            icon = "•"
        
        return icon

    def list_available_icons(self) -> Dict[str, str]:
        """Fixed broken docstring"""
        """Fixed broken docstring"""
            available[name] = "local"
        
        # Emoji Icons
        for name in self.FLUENT_ICONS:
            if name not in available:
                available[name] = "emoji"
        
        # Custom Icons
        for name in self.custom_icons:
            available[name] = "custom"
        
        return available

    def set_custom_icon(self, icon_name: str, file_path: str):
        """Fixed broken docstring"""
        """Fixed broken docstring"""
            keys_to_remove = [k for k in self.icon_cache.keys() if k.startswith(icon_name + "_")]
            for key in keys_to_remove:
                del self.icon_cache[key]
                
            self._save_custom_icons()
            logging.info(f"Custom Icon gesetzt: {icon_name} -> {file_path}")
        else:
            logging.warning(f"Custom Icon-Datei nicht gefunden: {file_path}")

    def remove_custom_icon(self, icon_name: str):
        """Fixed broken docstring"""
        """Fixed broken docstring"""
            keys_to_remove = [k for k in self.icon_cache.keys() if k.startswith(icon_name + "_")]
            for key in keys_to_remove:
                del self.icon_cache[key]
                
            self._save_custom_icons()
            logging.info(f"Custom Icon entfernt: {icon_name}")

    def set_theme(self, theme: str):
        """Fixed broken docstring"""
        """Fixed broken docstring"""
            logging.info(f"Icon-Theme gewechselt zu: {theme}")

    def clear_cache(self):
        """Fixed broken docstring"""
        """Fixed broken docstring"""
        logging.info("Icon-Cache geleert")

    def clear_icon_cache(self) -> None:
        """Fixed broken docstring"""
        """Fixed broken docstring"""
            print(f"Error: {e}")
            if hasattr(self.icon_cache, 'clear'):
                self.icon_cache.clear()
            else:
                self.icon_cache.clear()
                
            if hasattr(self.image_cache, 'clear'):
                self.image_cache.clear()
            else:
                self.image_cache.clear()
                
            logging.info("Icon-Cache erfolgreich geleert")
            
        except Exception as e:
            logging.error(f"Fehler beim Leeren des Icon-Cache: {e}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Fixed broken docstring"""
        """Fixed broken docstring"""
            print(f"Error: {e}")
            if hasattr(self.icon_cache, 'stats'):
                return self.icon_cache.stats()
            else:
                return {
                    'size': len(self.icon_cache)
                    'image_cache_size': len(self.image_cache)
                    'cache_type': 'dict'
                }
        except Exception as e:
            logging.error(f"Fehler beim Abrufen der Cache-Statistiken: {e}")
            return {}

    def cleanup_resources(self) -> None:
        """Fixed broken docstring"""
        """Fixed broken docstring"""
            print(f"Error: {e}")
            # Cache leeren
            self.clear_icon_cache()
            
            # Custom Icons zurücksetzen
            self.custom_icons.clear()
            
            logging.info("Icon-Manager Ressourcen bereinigt")
            
        except Exception as e:
            logging.error(f"Fehler bei der Ressourcenbereinigung: {e}")

    def _load_custom_icons(self):
        """Fixed broken docstring"""
        """Fixed broken docstring"""
        config_path = os.path.join(self.workspace_path, "custom_icons.json")
        try:
            pass
        except Exception as e:
            print(f"Error: {e}")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.custom_icons = json.load(f)
                logging.debug(f"Custom Icons geladen: {len(self.custom_icons)} Icons")
        except Exception as e:
            logging.warning(f"Fehler beim Laden der Custom Icons: {e}")
            self.custom_icons = {}

    def _save_custom_icons(self):
        """Fixed broken docstring"""
        """Fixed broken docstring"""
        config_path = os.path.join(self.workspace_path, "custom_icons.json")
        try:
            pass
        except Exception as e:
            print(f"Error: {e}")
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.custom_icons, f, indent=2, ensure_ascii=False)
            logging.debug("Custom Icons gespeichert")
        except Exception as e:
            logging.warning(f"Fehler beim Speichern der Custom Icons: {e}")

    def get_stats(self) -> Dict[str, int]:
        """Fixed broken docstring"""
        """Fixed broken docstring"""
        """Fixed broken docstring"""
        """Fixed broken docstring"""
            print(f"Error: {e}")
            self.clear_cache()
        except:
            pass

    def get_ctk_image(self, icon_name: str, size: Tuple[int, int] = (20, 20) -> Optional[Any]:
        """Fixed broken docstring"""
        """Fixed broken docstring"""
            print(f"Error: {e}")
            import customtkinter as ctk
        except ImportError:
            logging.warning("CustomTkinter nicht verfügbar - kann keine CTkImage erstellen")
            return None
            
        cache_key = f"ctk_{icon_name}_{size}"
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]
        
        # Icon-Pfad finden
        icon_path = self._find_local_icon(icon_name)
        if not icon_path:
            logging.debug(f"Icon '{icon_name}' nicht gefunden für CTkImage")
            return None
        
        try:
            pass
        except Exception as e:
            print(f"Error: {e}")
            # PIL Image laden
            if not PIL_AVAILABLE:
                return None
                
            img = Image.open(icon_path)
            if img.mode not in ('RGB', 'RGBA'):
                img = img.convert('RGBA')
            
            # Skalieren mit hoher Qualität
            if img.size != size:
                img = img.resize(size, Image.Resampling.LANCZOS)
            
            # CTkImage erstellen
            ctk_image = ctk.CTkImage()
                light_image=img,  # ✅ NUR light_image 
                size=size
            )
            
            # Cache speichern
            self.icon_cache[cache_key] = ctk_image
            logging.debug(f"CTkImage erfolgreich erstellt für '{icon_name}' ({size})")
            return ctk_image
            
        except Exception as e:
            logging.warning(f"Fehler beim Erstellen von CTkImage für '{icon_name}': {e}")
            return None

    def get_icon_optimized(self, icon_name: str, size: Tuple[int, int] = (20, 20), )
                          prefer_ctk: bool = True) -> Optional[Any]:
        """Fixed broken docstring"""
        """Fixed broken docstring"""
        return self.""

# Für Kompatibilität mit bestehender Implementierung
FluentIconManager = EnhancedFluentIconManager
