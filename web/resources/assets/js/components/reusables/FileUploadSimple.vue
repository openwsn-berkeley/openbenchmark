
<template>
    <div class="example-simple">
        <div class="upload">
            <ul v-if="files.length > 0">
                <li v-for="(file, index) in files" :key="file.id">
                    <span class="ellipsis">{{file.name}}</span> -
                    <span>{{file.size | formatSize}}</span> -
                    <span v-if="file.error">{{file.error}}</span>
                    <span v-else-if="file.success">success</span>
                    <span v-else-if="file.active">active</span>
                    <span v-else-if="file.active">active</span>
                    <span v-else></span>
                </li>
            </ul>
            <div class="example-btn">
                <file-upload
                    class=""
                    post-action="/api/firmware-upload"
                    :multiple="false"
                    :size="1024 * 1024 * 10"
                    v-model="files"
                    @input-filter="inputFilter"
                    @input-file="inputFile"
                    ref="upload">

                    <i class="fa fa-plus"></i>
                    <span style="font-size: 100%">Select files</span>
                </file-upload>
                <br>
                <button :disabled="allowUpload" type="button" class="main-btn btn-small" style="margin-top: 5px;" v-if="!$refs.upload || !$refs.upload.active" @click.prevent="$refs.upload.active = true">
                    <i class="fa fa-arrow-up" aria-hidden="true"></i>
                    Start Upload
                </button>
                <button type="button" class="main-btn btn-small btn-danger" style="margin-top: 5px;" v-else @click.prevent="$refs.upload.active = false">
                    <i class="fa fa-stop" aria-hidden="true"></i>
                    Stop Upload
                </button>
            </div>
        </div>
    </div>
</template>
<style>
    .example-simple label.btn {
        margin-bottom: 0;
        margin-right: 1rem;
    }
</style>

<script>
    import FileUpload from 'vue-upload-component'
    export default {
        components: {
            FileUpload,
        },
        props: [
            'allow-upload'
        ],
        data() {
            return {
                files: [],
            }
        },
        methods: {
            inputFilter(newFile, oldFile, prevent) {
                if (newFile && !oldFile) {
                    // Before adding a file
                    // Filter system files or hide files
                    if (/(\/|^)(Thumbs\.db|desktop\.ini|\..+)$/.test(newFile.name)) {
                        return prevent()
                    }
                    // Filter php html js file
                    if (/\.(php5?|html?|jsx?)$/i.test(newFile.name)) {
                        return prevent()
                    }
                }
            },
            inputFile(newFile, oldFile) {
                if (newFile && !oldFile) {
                    this.processResponse(newFile)
                    console.log('add')
                }
                if (newFile && oldFile) {
                    this.processResponse(newFile)
                    console.log('update')
                }
                if (!newFile && oldFile) {
                    // remove
                    console.log('remove')
                }
            },

            processResponse(newFile) {
                if (newFile.xhr && newFile.xhr.status > 0) {
                    this.$eventHub.$emit('FIRMWARE_UPLOADED', newFile.response)
                } else {
                    console.log('Firmware upload failed')
                }
            }
        },

        filters: {
            formatSize(size) {
                if (size > 1024 * 1024 * 1024 * 1024) {
                    return (size / 1024 / 1024 / 1024 / 1024).toFixed(2) + ' TB'
                } else if (size > 1024 * 1024 * 1024) {
                    return (size / 1024 / 1024 / 1024).toFixed(2) + ' GB'
                } else if (size > 1024 * 1024) {
                    return (size / 1024 / 1024).toFixed(2) + ' MB'
                } else if (size > 1024) {
                    return (size / 1024).toFixed(2) + ' KB'
                }
                
                return size.toString() + ' B'
            }
        }

    }
</script>

<style></style>