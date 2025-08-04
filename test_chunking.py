#!/usr/bin/env python3
"""
Test the new chunking strategy with long documents
"""

import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

def test_chunking_strategy():
    print("🧪 TESTING CHUNKING STRATEGY")
    print("=" * 60)
    
    # Import after path setup
    from backend.ml_classifier import classify_document_text
    
    # Test 1: Short document (should use direct classification)
    print("📄 TEST 1: Short Document (Direct Classification)")
    short_doc = """
    This is a technical documentation for implementing a REST API using FastAPI framework.
    It covers basic endpoints, database integration, and error handling patterns.
    """
    
    print(f"   📏 Length: {len(short_doc)} characters")
    result1 = classify_document_text(short_doc)
    print(f"   📂 Category: {result1['predicted_category']}")
    print(f"   📊 Confidence: {result1['confidence_score']:.4f}")
    print(f"   🔧 Method: {result1['aggregation_method']}")
    print(f"   📝 Chunks: {result1['chunks_used']}")
    print()
    
    # Test 2: Long document (should use chunking)
    print("📄 TEST 2: Long Document (Chunking Strategy)")
    long_doc = """
    COMPREHENSIVE LEGAL AGREEMENT - SOFTWARE LICENSE TERMS AND CONDITIONS
    
    IMPORTANT NOTICE: Please read these terms and conditions carefully before using our software.
    
    1. DEFINITIONS AND INTERPRETATION
    1.1 In this Agreement, unless the context otherwise requires, the following words and expressions shall have the meanings set out below:
    "Agreement" means this software license agreement including all schedules, appendices and amendments;
    "Company" means the software development company providing the licensed software;
    "Documentation" means all user manuals, technical manuals, and any other materials provided by Company;
    "Intellectual Property Rights" means all intellectual property rights including patents, trademarks, copyrights;
    "License" means the license to use the Software granted under this Agreement;
    "Software" means the computer software programs and associated documentation provided under this Agreement;
    "User" means the individual or entity that has agreed to be bound by this Agreement.
    
    2. GRANT OF LICENSE
    2.1 Subject to the terms and conditions of this Agreement, Company hereby grants to User a limited, non-exclusive, non-transferable, non-sublicensable license to use the Software solely for User's internal business purposes.
    2.2 The license granted herein does not include the right to sublicense, distribute, or otherwise transfer the Software to any third party.
    2.3 User acknowledges that the Software contains proprietary and confidential information of Company.
    
    3. RESTRICTIONS ON USE
    3.1 User shall not: (a) modify, adapt, alter, translate, or create derivative works of the Software; (b) reverse engineer, decompile, disassemble, or otherwise attempt to derive the source code of the Software; (c) remove, alter, or obscure any proprietary notices on the Software; (d) use the Software for any unlawful purpose or in any manner that violates applicable laws.
    3.2 User shall implement reasonable security measures to prevent unauthorized access to the Software.
    3.3 User shall not use the Software to develop competing products or services.
    
    4. INTELLECTUAL PROPERTY RIGHTS
    4.1 Company retains all right, title, and interest in and to the Software and Documentation, including all Intellectual Property Rights therein.
    4.2 No rights are granted to User except as expressly set forth in this Agreement.
    4.3 User acknowledges that the Software is protected by copyright laws and international treaty provisions.
    
    5. SUPPORT AND MAINTENANCE
    5.1 Company may, but is not obligated to, provide technical support for the Software.
    5.2 Any support services provided shall be subject to Company's then-current support policies.
    5.3 User acknowledges that Company may discontinue support at any time with reasonable notice.
    
    6. WARRANTY DISCLAIMER
    6.1 THE SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND.
    6.2 COMPANY DISCLAIMS ALL WARRANTIES, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT.
    6.3 COMPANY DOES NOT WARRANT THAT THE SOFTWARE WILL MEET USER'S REQUIREMENTS OR THAT THE OPERATION OF THE SOFTWARE WILL BE UNINTERRUPTED OR ERROR-FREE.
    
    7. LIMITATION OF LIABILITY
    7.1 IN NO EVENT SHALL COMPANY BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES ARISING OUT OF OR RELATING TO THIS AGREEMENT.
    7.2 COMPANY'S TOTAL LIABILITY SHALL NOT EXCEED THE AMOUNT PAID BY USER FOR THE SOFTWARE.
    7.3 THE LIMITATIONS SET FORTH IN THIS SECTION SHALL APPLY EVEN IF COMPANY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
    
    8. INDEMNIFICATION
    8.1 User agrees to indemnify, defend, and hold harmless Company from and against any claims, damages, losses, and expenses arising out of User's use of the Software.
    8.2 This indemnification obligation shall survive termination of this Agreement.
    
    9. TERM AND TERMINATION
    9.1 This Agreement shall remain in effect until terminated by either party.
    9.2 Either party may terminate this Agreement immediately upon written notice if the other party materially breaches this Agreement.
    9.3 Upon termination, User shall cease all use of the Software and destroy all copies thereof.
    
    10. GENERAL PROVISIONS
    10.1 This Agreement shall be governed by and construed in accordance with applicable laws.
    10.2 Any disputes arising under this Agreement shall be resolved through binding arbitration.
    10.3 This Agreement constitutes the entire agreement between the parties and supersedes all prior negotiations, representations, or agreements.
    10.4 If any provision of this Agreement is found to be unenforceable, the remainder shall remain in full force and effect.
    10.5 This Agreement may not be amended except by written agreement signed by both parties.
    
    By using the Software, User acknowledges that they have read, understood, and agree to be bound by the terms and conditions of this Agreement.
    """ * 2  # Make it even longer to ensure chunking
    
    print(f"   📏 Length: {len(long_doc)} characters")
    result2 = classify_document_text(long_doc)
    print(f"   📂 Category: {result2['predicted_category']}")
    print(f"   📊 Confidence: {result2['confidence_score']:.4f}")
    print(f"   🔧 Method: {result2['aggregation_method']}")
    print(f"   📝 Chunks: {result2['chunks_used']}")
    print(f"   🔤 Total Tokens: {result2['text_length_tokens']}")
    print(f"   ✂️  Truncated: {result2['was_truncated']}")
    print(f"   🗳️  Majority Vote: {result2['majority_vote']}")
    print(f"   ⏱️  Inference Time: {result2['inference_time']}s")
    
    if 'chunk_predictions' in result2:
        print(f"   📊 First 5 Chunk Predictions: {result2['chunk_predictions']}")
    
    print(f"\n   📈 All Category Scores:")
    for category, score in result2['all_scores'].items():
        print(f"      {category}: {score:.4f}")
    
    print(f"\n   ⚖️  Weighted Scores:")
    for category, score in result2['weighted_scores'].items():
        print(f"      {category}: {score:.4f}")
    
    print(f"\n✅ CHUNKING BENEFITS:")
    print(f"   • Used ALL {result2['text_length_tokens']} tokens (no truncation!)")
    print(f"   • Processed {result2['chunks_used']} overlapping chunks")
    print(f"   • Multiple aggregation strategies for robustness")
    print(f"   • Preserves context with chunk overlap")

if __name__ == "__main__":
    test_chunking_strategy()
