 // async function base64ToCryptoKey(base64Key) {
 //        const rawKey = window.atob(base64Key);
 //        const keyBuffer = new Uint8Array(new ArrayBuffer(rawKey.length));
 //        for (let i = 0; i < rawKey.length; i++) {
 //            keyBuffer[i] = rawKey.charCodeAt(i);
 //        }
 //        return window.crypto.subtle.importKey(
 //            "raw",
 //            keyBuffer,
 //            {name: "AES-CBC", length: 256},
 //            true,
 //            ["encrypt", "decrypt"]
 //        );
 //    }
 //
 //    // 加密方法，调用：encryptString("明文","编码后的密钥")
 //    async function encryptString(str, base64Key) {
 //        try {
 //            const cryptoKey = await base64ToCryptoKey(base64Key);
 //            const iv = window.crypto.getRandomValues(new Uint8Array(16));
 //            const encoded = new TextEncoder().encode(str);
 //
 //            const encrypted = await window.crypto.subtle.encrypt(
 //                {name: "AES-CBC", iv},
 //                cryptoKey,
 //                encoded
 //            );
 //
 //            const ivAndEncrypted = new Uint8Array(iv.length + encrypted.byteLength);
 //            ivAndEncrypted.set(iv, 0);
 //            ivAndEncrypted.set(new Uint8Array(encrypted), iv.length);
 //
 //            return window.btoa(String.fromCharCode.apply(null, ivAndEncrypted));
 //        } catch (error) {
 //            throw new Error('加密过程中发生错误');
 //        }
 //    }
 //
 //
 //    // 解密方法，调用：decryptString("编码后的密文","编码后的密钥")
 //    async function decryptString(encryptedBase64Str, base64Key) {
 //        try {
 //            const cryptoKey = await base64ToCryptoKey(base64Key);
 //            const ivAndEncrypted = Uint8Array.from(atob(encryptedBase64Str), c => c.charCodeAt(0));
 //            const iv = ivAndEncrypted.slice(0, 16);
 //            const encrypted = ivAndEncrypted.slice(16);
 //
 //            const decrypted = await window.crypto.subtle.decrypt(
 //                {name: "AES-CBC", iv},
 //                cryptoKey,
 //                encrypted
 //            );
 //
 //            return new TextDecoder().decode(decrypted);
 //        } catch (error) {
 //            throw new Error('解密过程中发生错误');
 //        }
 //    }