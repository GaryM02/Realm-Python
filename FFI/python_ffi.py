from ctypes import *
import faulthandler
# Load the shared library into ctypes
libname = "./FFI/librealm-ffi-dbg.dylib"
realm_ffi = cdll.LoadLibrary(libname)

#/classes and properties for testing

#define class info
# typedef struct realm_class_info {
#     const char* name;
#     const char* primary_key;
#     size_t num_properties;
#     size_t num_computed_properties;
#     realm_class_key_t key;
#     int flags;
# } realm_class_info_t;


class Class_Info(Structure):
    _fields_ = [("name", c_wchar_p), ("primary_key", c_wchar_p),
                ("num_properties", c_int), ("num_computed_properties", c_int),
                ("key", c_int)]


#define property info
# typedef struct realm_property_info {
#     const char* name;
#     const char* public_name;
#     realm_property_type_e type;
#     realm_collection_type_e collection_type;
#     const char* link_target;
#     const char* link_origin_property_name;
#     realm_property_key_t key;
#     int flags;
# } realm_property_info_t;
class Property_Info(Structure):
    _fields_ = [("name", c_wchar_p), ("public_name", c_wchar_p),
                ("type", c_int), ("collection_type", c_int),
                ("link_target", c_wchar_p),
                ("link_origin_property_name", c_wchar_p),
                ("realm_property_key_t", c_int), ("flags", c_int)]


#/end of classes and properties


#define error check for last error
# typedef struct realm_error {
#     realm_errno_e error;
#     const char* message;
#     // When error is RLM_ERR_CALLBACK this is an opaque pointer to an SDK-owned error object
#     // thrown by user code inside a callback with realm_register_user_code_callback_error(), otherwise null.
#     void* usercode_error;
#     union {
#         int code;
#         realm_logic_error_kind_e logic_error_kind;
#     } kind;
# } realm_error_t;
class Error(Structure):
    _fields_ = [("error", c_int), ("message", c_char_p),
                ("usercode_error", c_char_p), ("kind", c_int)]


def check_error():
    err = Error()
    realm_ffi.realm_get_last_error.argtypes = [POINTER(Error)]
    realm_ffi.realm_get_last_error(byref(err))
    print(err.message)


#define schema
# /**
#  * Create a new schema from classes and their properties.
#  *
#  * Note: This function does not validate the schema.
#  *
#  * Note: `realm_class_key_t` and `realm_property_key_t` values inside
#  *       `realm_class_info_t` and `realm_property_info_t` are unused when
#  *       defining the schema. Call `realm_get_schema()` to obtain the values for
#  *       these fields in an open realm.
#  *
#  * @return True if allocation of the schema structure succeeded.
#  */
# RLM_API realm_schema_t* realm_schema_new(const realm_class_info_t* classes, size_t num_classes,
#                                          const realm_property_info_t** class_properties);
class Schema():
    def __init__(self):
        classes = (Class_Info * 1)
        ii = classes(Class_Info("", "", 2, 0, 0))
        class_properties = ((Property_Info * 2) * 1)
        xx = class_properties(
            (Property_Info("id", "id", 0,
                           0), Property_Info("text", "text", 2, 0)))
        realm_ffi.realm_schema_new.restype = c_void_p
        self.handle = realm_ffi.realm_schema_new(ii, 0, xx)
        print(self.handle)


#define configuration
# /**
#  * Allocate a new configuration with default options.
#  */
# RLM_API realm_config_t* realm_config_new(void);
class Configuration():
    def __init__(self, schema):
        realm_ffi.realm_config_new.restype = c_void_p
        self.handle = realm_ffi.realm_config_new()
        set_schema_object(c_void_p(self.handle), c_void_p(schema.handle))
        set_schema_version(c_void_p(self.handle))
        encoded_file = "example.realm".encode('utf-8')
        set_path_for_realm(c_void_p(self.handle), c_char_p(encoded_file))


#set schema object for realm
# /**
#  * Set the schema object for this realm.
#  *
#  * This does not take ownership of the schema object, and it should be released
#  * afterwards.
#  *
#  * This function aborts when out of memory, but otherwise cannot fail.
#  *
#  * @param schema The schema object. May be NULL, which means an empty schema.
#  */
# RLM_API void realm_config_set_schema(realm_config_t*, const realm_schema_t* schema);
def set_schema_object(handle, schema):
    realm_ffi.realm_config_set_schema.restype = c_void_p
    realm_ffi.realm_config_set_schema(handle, schema)


# #set schema version for realm
# /**
#  * Set the schema version of the schema.
#  *
#  * This function cannot fail.
#  */
# RLM_API void realm_config_set_schema_version(realm_config_t*, uint64_t version);
def set_schema_version(handle):
    realm_ffi.realm_config_set_schema_version.restype = c_void_p
    realm_ffi.realm_config_set_schema_version(handle, 1)


#define path for realm file
# /**
#  * Set the path of the realm being opened.
#  *
#  * This function aborts when out of memory, but otherwise cannot fail.
#  */
# RLM_API void realm_config_set_path(realm_config_t*, const char* path);
def set_path_for_realm(handle, encoded_file):
    realm_ffi.realm_config_set_path.restype = c_void_p
    realm_ffi.realm_config_set_path(handle, encoded_file)


#define our realm
class Realm():
    def __init__(self, configuration):
        self.configuration = configuration

        #open the realm
        # /**
        #  * Open a Realm file.
        #  *
        #  * @param config Realm configuration. If the Realm is already opened on another
        #  *               thread, validate that the given configuration is compatible
        #  *               with the existing one.
        #  * @return If successful, the Realm object. Otherwise, NULL.
        #  */
        # RLM_API realm_t* realm_open(const realm_config_t* config);

        realm_ffi.realm_open.restype = c_void_p
        self.handle = realm_ffi.realm_open(c_void_p(self.configuration.handle))
        print(self.handle)

    #release realm pointer owned by caller
    # /**
    # * Free any Realm C Wrapper object.
    # *
    # * Note: Any pointer returned from a library function is owned by the caller.
    # *       The caller is responsible for calling `realm_release()`. The only
    # *       exception from this is C++ bridge functions that return `void*`, with
    # *       the prefix `_realm`.
    # *
    # * Note: C++ destructors are typically `noexcept`, so it is likely that an
    # *       exception will crash the process.
    # *
    # * @param ptr A pointer to a Realm C Wrapper object. May be NULL.
    # */
    # RLM_API void realm_release(void* ptr);
    def realm_release(self):
        realm_ffi.realm_release.restype = c_void_p
        realm_ffi.realm_release(c_void_p(self.configuration.handle))

    #begin write transaction
    # /**
    # * Begin a write transaction for the Realm file.
    # *
    # * @return True if no exception occurred.
    # */
    # RLM_API bool realm_begin_write(realm_t*);
    def begin_write(self):
        Realm.begin_read(self.handle)
        assert realm_ffi.realm_begin_write(c_void_p(self.handle))
        print("begin")

    #begin a read transaction
    # /**
    # * Begin a read transaction for the Realm file.
    # *
    # * @return True if no exception occurred.
    # */
    # RLM_API bool realm_begin_read(realm_t*);
    def begin_read(handle):
        realm_ffi.realm_begin_read.restype = c_bool
        assert realm_ffi.realm_begin_read(c_void_p(handle))

    #check if realm is closed
    # /**
    # * True if the Realm file is closed.
    # *
    # * This function cannot fail.
    # */
    # RLM_API bool realm_is_closed(realm_t*);
    def realm_is_closed(self):
        realm_ffi.realm_is_closed.restype = c_bool
        closed = realm_ffi.realm_is_closed(c_void_p(self.handle))
        if closed == False:
            print("The realm is not closed.")
        else:
            print("The realm is closed.")

    def realm_is_frozen(self):
        realm_ffi.realm_is_frozen.restype = c_bool
        frozen = realm_ffi.realm_is_frozen(c_void_p(self.handle))
        if frozen == False:
            print("The realm is not frozen.")
        else:
            print("The realm is frozen.")


#check if realm is writeable
# /**
# * Return true if the realm is in a write transaction.
# *
# * This function cannot fail.
# */
# RLM_API bool realm_is_writable(const realm_t*);
def realm_is_writable():
    pass


config = Configuration(Schema())
realm = Realm(config)
realm.begin_write()
realm.realm_is_closed()
realm.realm_is_frozen()
check_error()
