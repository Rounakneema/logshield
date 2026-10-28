import re

# All 38 references with metadata
raw_references = [
    {
        "old_id": 1,
        "year": 2024,
        "authors": "Kubernetes Authors",
        "title": "Pods and sidecar containers",
        "citation": 'Kubernetes Authors, "Pods and sidecar containers," Kubernetes Documentation, 2024. [Online]. Available: https://kubernetes.io/docs/concepts/workloads/pods/'
    },
    {
        "old_id": 2,
        "year": 2016,
        "authors": "T. Barik, R. DeLine, S. Drucker, and D. Fisher",
        "title": "The bones of the system",
        "citation": 'T. Barik, R. DeLine, S. Drucker, and D. Fisher, "The bones of the system: A case study of logging and telemetry at Microsoft," in Proc. 38th Int. Conf. Softw. Eng. Companion (ICSE-C), 2016, pp. 92–101.'
    },
    {
        "old_id": 3,
        "year": 2025,
        "authors": "R. Aghili, H. Li, and F. Khomh",
        "title": "Protecting privacy in software logs: What should be anonymized?",
        "citation": 'R. Aghili, H. Li, and F. Khomh, "Protecting privacy in software logs: What should be anonymized?," Proc. ACM Softw. Eng., vol. 2, no. ISSTA, pp. 1317–1338, 2025.'
    },
    {
        "old_id": 4,
        "year": 2024,
        "authors": "Datadog Inc.",
        "title": "Observability pipeline sizing and architecture guidelines",
        "citation": 'Datadog Inc., "Observability pipeline sizing and architecture guidelines," Datadog Technical Documentation, 2024. [Online]. Available: https://docs.datadoghq.com/observability_pipelines/'
    },
    {
        "old_id": 5,
        "year": 2020,
        "authors": "C. Zhi, J. Yin, J. Han, and S. Deng",
        "title": "A preliminary study on sensitive information exposure through logging",
        "citation": 'C. Zhi, J. Yin, J. Han, and S. Deng, "A preliminary study on sensitive information exposure through logging," in Proc. 27th Asia-Pacific Softw. Eng. Conf. (APSEC), 2020, pp. 470–474.'
    },
    {
        "old_id": 6,
        "year": 2025,
        "authors": "Z. Wahab, S. Ahmed, M. N. Rahman, R. Shahriyar, and G. Uddin",
        "title": "Secret leak detection in software issue reports using LLMs: A comprehensive evaluation",
        "citation": 'Z. Wahab, S. Ahmed, M. N. Rahman, R. Shahriyar, and G. Uddin, "Secret leak detection in software issue reports using LLMs: A comprehensive evaluation," in Proc. IEEE/ACM Int. Conf. Mining Softw. Repositories (MSR), 2025; also arXiv:2410.23657, 2024.'
    },
    {
        "old_id": 7,
        "year": 2019,
        "authors": "A. O. Portillo-Dominguez and V. Ayala-Rivera",
        "title": "Towards an efficient log data protection in software systems",
        "citation": 'A. O. Portillo-Dominguez and V. Ayala-Rivera, "Towards an efficient log data protection in software systems through data minimization and anonymization," in Proc. 7th Int. Conf. Softw. Eng. Res. Innov. (CONISOFT), 2019, pp. 107–115.'
    },
    {
        "old_id": 8,
        "year": 2023,
        "authors": "M. Khoje",
        "title": "Securing data platforms: Strategic masking techniques",
        "citation": 'M. Khoje, "Securing data platforms: Strategic masking techniques for privacy and security for B2B enterprise data," Int. J. Comput. Trends Technol. (IJCTT), vol. 71, no. 11, pp. 46–54, Nov. 2023.'
    },
    {
        "old_id": 9,
        "year": 2022,
        "authors": "MITRE Corporation",
        "title": "CWE-532: Insertion of sensitive information into log file",
        "citation": 'MITRE Corporation, "CWE-532: Insertion of sensitive information into log file," Common Weakness Enumeration, 2022. [Online]. Available: https://cwe.mitre.org/data/definitions/532.html'
    },
    {
        "old_id": 10,
        "year": 2023,
        "authors": "MITRE Corporation",
        "title": "CWE-798: Use of hard-coded credentials",
        "citation": 'MITRE Corporation, "CWE-798: Use of hard-coded credentials," Common Weakness Enumeration, 2023. [Online]. Available: https://cwe.mitre.org/data/definitions/798.html'
    },
    {
        "old_id": 11,
        "year": 2023,
        "authors": "GitGuardian",
        "title": "The state of secrets sprawl 2023",
        "citation": 'GitGuardian, "The state of secrets sprawl 2023," GitGuardian, Mar. 2023. [Online]. Available: https://blog.gitguardian.com/the-state-of-secrets-sprawl-2023'
    },
    {
        "old_id": 12,
        "year": 2024,
        "authors": "Z. Rice",
        "title": "Gitleaks: Protect and discover secrets in code",
        "citation": 'Z. Rice, "Gitleaks: Protect and discover secrets in code," GitHub repository, 2024. [Online]. Available: https://github.com/gitleaks/gitleaks'
    },
    {
        "old_id": 13,
        "year": 2024,
        "authors": "D. Ayrey",
        "title": "TruffleHog: High entropy secret finder",
        "citation": 'D. Ayrey, "TruffleHog: High entropy secret finder," GitHub repository, 2024. [Online]. Available: https://github.com/trufflesecurity/trufflehog'
    },
    {
        "old_id": 14,
        "year": 2024,
        "authors": "Yelp Inc.",
        "title": "detect-secrets: An enterprise-friendly secrets detection module",
        "citation": 'Yelp Inc., "detect-secrets: An enterprise-friendly secrets detection module," GitHub repository, 2024. [Online]. Available: https://github.com/Yelp/detect-secrets'
    },
    {
        "old_id": 15,
        "year": 2016,
        "authors": "European Parliament and Council of the EU",
        "title": "General Data Protection Regulation (GDPR)",
        "citation": 'European Parliament and Council of the European Union, "Regulation (EU) 2016/679 on the protection of natural persons with regard to the processing of personal data (General Data Protection Regulation)," Official J. Eur. Union, vol. L119, pp. 1–88, May 2016.'
    },
    {
        "old_id": 16,
        "year": 1996,
        "authors": "U.S. Congress",
        "title": "Health Insurance Portability and Accountability Act of 1996 (HIPAA)",
        "citation": 'U.S. Congress, "Health Insurance Portability and Accountability Act of 1996," Pub. L. No. 104-191, 110 Stat. 1936, Aug. 1996.'
    },
    {
        "old_id": 17,
        "year": 2022,
        "authors": "PCI Security Standards Council",
        "title": "PCI Data Security Standard v4.0",
        "citation": 'PCI Security Standards Council, "Payment Card Industry (PCI) Data Security Standard: Requirements and testing procedures, version 4.0," PCI SSC, Mar. 2022.'
    },
    {
        "old_id": 18,
        "year": 2020,
        "authors": "Joint Task Force",
        "title": "NIST Special Publication 800-53, Rev. 5",
        "citation": 'Joint Task Force, "Security and privacy controls for information systems and organizations," Nat. Inst. Standards Technol., Gaithersburg, MD, USA, NIST Special Publication 800-53, Rev. 5, Sep. 2020.'
    },
    {
        "old_id": 19,
        "year": 2020,
        "authors": "A. Saha, T. Denning, V. Srikumar, and S. K. Kasera",
        "title": "Secrets in source code: Reducing false positives using machine learning",
        "citation": 'A. Saha, T. Denning, V. Srikumar, and S. K. Kasera, "Secrets in source code: Reducing false positives using machine learning," in Proc. 12th Int. Conf. Commun. Syst. Netw. (COMSNETS), Bengaluru, India, 2020, pp. 168–175.'
    },
    {
        "old_id": 20,
        "year": 2023,
        "authors": "S. K. Basak, L. Neil, B. Reaves, and L. Williams",
        "title": "SecretBench: A dataset of software secrets",
        "citation": 'S. K. Basak, L. Neil, B. Reaves, and L. Williams, "SecretBench: A dataset of software secrets," in Proc. IEEE/ACM 20th Int. Conf. Mining Softw. Repositories (MSR), 2023, pp. 347–351.'
    },
    {
        "old_id": 21,
        "year": 2023,
        "authors": "Fernet Specification",
        "title": "Fernet specification",
        "citation": '"Fernet specification," GitHub repository, 2023. [Online]. Available: https://github.com/fernet/spec'
    },
    {
        "old_id": 22,
        "year": 2001,
        "authors": "Nat. Inst. Standards Technol.",
        "title": "Advanced Encryption Standard (AES)",
        "citation": 'Nat. Inst. Standards Technol., "Advanced Encryption Standard (AES)," Federal Information Processing Standards Publication 197, Nov. 2001.'
    },
    {
        "old_id": 23,
        "year": 1997,
        "authors": "H. Krawczyk, M. Bellare, and R. Canetti",
        "title": "HMAC: Keyed-hashing for message authentication",
        "citation": 'H. Krawczyk, M. Bellare, and R. Canetti, "HMAC: Keyed-hashing for message authentication," Internet Eng. Task Force, RFC 2104, Feb. 1997.'
    },
    {
        "old_id": 24,
        "year": 2015,
        "authors": "Nat. Inst. Standards Technol.",
        "title": "Secure Hash Standard (SHS)",
        "citation": 'Nat. Inst. Standards Technol., "Secure Hash Standard (SHS)," Federal Information Processing Standards Publication 180-4, Aug. 2015.'
    },
    {
        "old_id": 25,
        "year": 2024,
        "authors": "Kubernetes Authors",
        "title": "Network policies",
        "citation": 'Kubernetes Authors, "Network policies," Kubernetes Documentation, 2024. [Online]. Available: https://kubernetes.io/docs/concepts/services-networking/network-policies/'
    },
    {
        "old_id": 26,
        "year": 2023,
        "authors": "J. Zhu, S. He, P. He, J. Liu, and M. R. Lyu",
        "title": "Loghub: A large collection of system log datasets for AI-driven log analytics",
        "citation": 'J. Zhu, S. He, P. He, J. Liu, and M. R. Lyu, "Loghub: A large collection of system log datasets for AI-driven log analytics," in Proc. 34th IEEE Int. Symp. Softw. Rel. Eng. (ISSRE), 2023, pp. 355–366.'
    },
    {
        "old_id": 27,
        "year": 2004,
        "authors": "A. J. Slagell and W. Yurcik",
        "title": "Sharing computer network logs for security and privacy",
        "citation": 'A. J. Slagell and W. Yurcik, "Sharing computer network logs for security and privacy: A motivation for new methodologies of anonymization," arXiv:cs/0409005, 2004.'
    },
    {
        "old_id": 28,
        "year": 2006,
        "authors": "A. J. Slagell, K. Lakkaraju, and K. Luo",
        "title": "FLAIM: A multi-level anonymization framework for computer and network logs",
        "citation": 'A. J. Slagell, K. Lakkaraju, and K. Luo, "FLAIM: A multi-level anonymization framework for computer and network logs," in Proc. 20th USENIX Large Installation Syst. Admin. Conf. (LISA), 2006, pp. 3–8.'
    },
    {
        "old_id": 29,
        "year": 2019,
        "authors": "M. Meli, M. R. McNiece, and B. Reaves",
        "title": "How bad can it git? Characterizing secret leakage in public GitHub repositories",
        "citation": 'M. Meli, M. R. McNiece, and B. Reaves, "How bad can it git? Characterizing secret leakage in public GitHub repositories," in Proc. Netw. Distrib. Syst. Security Symp. (NDSS), 2019, pp. 1–15.'
    },
    {
        "old_id": 30,
        "year": 2025,
        "authors": "M. N. Rahman, S. Ahmed, Z. Wahab, S. M. Sohan, and R. Shahriyar",
        "title": "Secret breach detection in source code with large language models",
        "citation": 'M. N. Rahman, S. Ahmed, Z. Wahab, S. M. Sohan, and R. Shahriyar, "Secret breach detection in source code with large language models," in Proc. 19th ACM/IEEE Int. Symp. Empirical Softw. Eng. Meas. (ESEM), 2025; also arXiv:2504.18784, 2025.'
    },
    {
        "old_id": 31,
        "year": 2024,
        "authors": "Y. Huang, Y. Li, W. Wu, J. Zhang, and M. R. Lyu",
        "title": "Your code secret belongs to me: Neural code completion tools can memorize hard-coded credentials",
        "citation": 'Y. Huang, Y. Li, W. Wu, J. Zhang, and M. R. Lyu, "Your code secret belongs to me: Neural code completion tools can memorize hard-coded credentials," Proc. ACM Softw. Eng., vol. 1, no. FSE, Art. 111, pp. 1–23, Jul. 2024.'
    },
    {
        "old_id": 32,
        "year": 1975,
        "authors": "A. V. Aho and M. J. Corasick",
        "title": "Efficient string matching: An aid to bibliographic search",
        "citation": 'A. V. Aho and M. J. Corasick, "Efficient string matching: An aid to bibliographic search," Commun. ACM, vol. 18, no. 6, pp. 333–340, Jun. 1975.'
    },
    {
        "old_id": 33,
        "year": 1948,
        "authors": "C. E. Shannon",
        "title": "A mathematical theory of communication",
        "citation": 'C. E. Shannon, "A mathematical theory of communication," Bell Syst. Tech. J., vol. 27, no. 3, pp. 379–423, Jul. 1948.'
    },
    {
        "old_id": 34,
        "year": 1989,
        "authors": "D. C. Liu and J. Nocedal",
        "title": "On the limited memory BFGS method for large scale optimization",
        "citation": 'D. C. Liu and J. Nocedal, "On the limited memory BFGS method for large scale optimization," Math. Program., vol. 45, nos. 1–3, pp. 503–528, Aug. 1989.'
    },
    {
        "old_id": 35,
        "year": 2005,
        "authors": "T. Berners-Lee, R. Fielding, and L. Masinter",
        "title": "Uniform Resource Identifier (URI): Generic syntax",
        "citation": 'T. Berners-Lee, R. Fielding, and L. Masinter, "Uniform Resource Identifier (URI): Generic syntax," Internet Eng. Task Force, RFC 3986, Jan. 2005.'
    },
    {
        "old_id": 36,
        "year": 1947,
        "authors": "Q. McNemar",
        "title": "Note on the sampling error of the difference between correlated proportions",
        "citation": 'Q. McNemar, "Note on the sampling error of the difference between correlated proportions or percentages," Psychometrika, vol. 12, no. 2, pp. 153–157, Jun. 1947.'
    },
    {
        "old_id": 37,
        "year": 1983,
        "authors": "J. A. Hanley and A. Lippman-Hand",
        "title": "If nothing goes wrong, is everything all right?",
        "citation": 'J. A. Hanley and A. Lippman-Hand, "If nothing goes wrong, is everything all right? Interpreting zero numerators," JAMA, vol. 249, no. 13, pp. 1743–1745, Apr. 1983.'
    },
    {
        "old_id": 38,
        "year": 1934,
        "authors": "C. J. Clopper and E. S. Pearson",
        "title": "The use of confidence or fiducial limits illustrated in the case of the binomial",
        "citation": 'C. J. Clopper and E. S. Pearson, "The use of confidence or fiducial limits illustrated in the case of the binomial," Biometrika, vol. 26, no. 4, pp. 404–413, Dec. 1934.'
    }
]

# Separate into recent (>= 2022) and older (< 2022)
recent = [r for r in raw_references if r["year"] >= 2022]
older = [r for r in raw_references if r["year"] < 2022]

# Sort recent descending: 2025, 2024, 2023, 2022
recent.sort(key=lambda x: (-x["year"], x["authors"]))

# Sort older descending: 2020, 2019, 2016, ... down to 1934
older.sort(key=lambda x: (-x["year"], x["authors"]))

sorted_refs = recent + older
print(f"Total sorted references: {len(sorted_refs)}")
print(f"Recent (>= 2022) count: {len(recent)} (Requires at least 15 -> {'PASSED' if len(recent) >= 15 else 'FAIL'})")
print(f"Older (< 2022) count: {len(older)}")

# Build mapping from old_id to new_id (1-based)
old_to_new = {}
for new_idx, r in enumerate(sorted_refs, 1):
    old_to_new[r["old_id"]] = new_idx
    print(f"[{new_idx}] (Old [{r['old_id']}], {r['year']}) {r['authors']}: {r['title']}")
